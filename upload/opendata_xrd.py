import os
import datetime
import sys
import re
from pathlib import Path
import shlex
import shutil
import uuid
import time
from typing import Optional, Union
from alienpy.tools_nowb import GetHumanReadableSize

HAS_XROOTD = False
XRDCP_CMD = None
HAS_XROOTD_GETDEFAULT = False

from rich.pretty import pprint

def XRD_EnvPut(key: str, value: str) -> bool:  # noqa: ANN001,ANN201
    """Sets the given key in the xrootd client environment to the given value.
    Returns false if there is already a shell-imported setting for this key, true otherwise
    """
    if not key or not value: return False
    if HAS_XROOTD:
        return xrd_client.EnvPutInt(key, int(value)) if ( str(value).isdigit() or isinstance(value, int) ) else xrd_client.EnvPutString(key, str(value))
    return False


def XRD_EnvGet(key: str) -> Union[None, int, str]:  # noqa: ANN001,ANN201
    """Get the value of the key from xrootd"""
    if not key: return None
    val = None
    if not HAS_XROOTD: return None
    val = xrd_client.EnvGetString(key)
    if not val:
        val = xrd_client.EnvGetInt(key)
    return val  # noqa: R504


def xrd_config_init(do_xrd_env_set: bool = True) -> None:
    """Initialize generic XRootD client vars/timeouts"""
    if not HAS_XROOTD: return
    # xrdcp parameters (used by ALICE tests)
    # http://xrootd.org/doc/man/xrdcp.1.html
    # https://xrootd.slac.stanford.edu/doc/xrdcl-docs/www/xrdcldocs.html#x1-100004.2
    # xrootd defaults https://github.com/xrootd/xrootd/blob/master/src/XrdCl/XrdClConstants.hh

    # Override the application name reported to the xrootd server.
    app_str = f'ALICE OpenData upload tool'
    XRD_EnvPut('AppName', app_str)
    os.environ['XRD_APPNAME'] = app_str

    # Resolution for the timeout events. Ie. timeout events will be processed only every XRD_TIMEOUTRESOLUTION seconds.
    timeout_resolution = os.getenv('XRD_TIMEOUTRESOLUTION', '1')  # let's check the status every 1s; default 15
    os.environ['XRD_TIMEOUTRESOLUTION'] = timeout_resolution
    XRD_EnvPut('TimeoutResolution', int(timeout_resolution))

    # Number of connection attempts that should be made (number of available connection windows) before declaring a permanent failure.
    con_retry = os.getenv('XRD_CONNECTIONRETRY', '3')  # default 5
    os.environ['XRD_CONNECTIONRETRY'] = con_retry
    XRD_EnvPut('ConnectionRetry', int(con_retry))

    # A time window for the connection establishment. A connection failure is declared if the connection is not established within the time window.
    # N.B.!!. If a connection failure happens earlier then another connection attempt will only be made at the beginning of the next window
    con_window = os.getenv('XRD_CONNECTIONWINDOW', '10')  # default 120
    os.environ['XRD_CONNECTIONWINDOW'] = con_window
    XRD_EnvPut('ConnectionWindow', int(con_window))

    # Default value for the time after which an error is declared if it was impossible to get a response to a request.
    # N.B.!!. This is the total time for the initialization dialogue!! see https://xrootd.slac.stanford.edu/doc/xrdcl-docs/www/xrdcldocs.html#x1-580004.3.6
    req_timeout = os.getenv('XRD_REQUESTTIMEOUT', '1200')  # default 1800; 1200s = 20min, 20 GB for 1MB/s
    os.environ['XRD_REQUESTTIMEOUT'] = req_timeout
    XRD_EnvPut('RequestTimeout', int(req_timeout))

    # Default value for the time after which a connection error is declared (and a recovery attempted) if there are unfulfilled requests and there is no socket activity or a registered wait timeout.
    # N.B.!!. we actually want this timeout for failure on onverloaded/unresponsive server. see https://github.com/xrootd/xrootd/issues/1597#issuecomment-1064081574
    stream_timeout = os.getenv('XRD_STREAMTIMEOUT', '60')  # default 60
    os.environ['XRD_STREAMTIMEOUT'] = stream_timeout
    XRD_EnvPut('StreamTimeout', int(stream_timeout))

    # Maximum time allowed for the copy process to initialize, ie. open the source and destination files.
    cpinit_timeout = os.getenv('XRD_CPINITTIMEOUT', '90')  # default 600
    os.environ['XRD_CPINITTIMEOUT'] = cpinit_timeout
    XRD_EnvPut('CPInitTimeout', int(cpinit_timeout))

    # Time period after which an idle connection to a data server should be closed.
    datasrv_ttl = os.getenv('XRD_DATASERVERTTL', '20')  # we have no reasons to keep idle connections
    os.environ['XRD_DATASERVERTTL'] = datasrv_ttl
    XRD_EnvPut('DataServerTTL', int(datasrv_ttl))

    # Time period after which an idle connection to a manager or a load balancer should be closed.
    loadbl_ttl = os.getenv('XRD_LOADBALANCERTTL', '30')  # we have no reasons to keep idle connections
    os.environ['XRD_LOADBALANCERTTL'] = loadbl_ttl
    XRD_EnvPut('LoadBalancerTTL', int(loadbl_ttl))

    # https://github.com/xrootd/xrootd/blob/v5.6.3/docs/man/xrdcp.1#L592
    # If set to 1, use the checksum available in a metalink file even if a file is being extracted from a ZIP archive.
    zip_mt_cksum = os.getenv('XRD_ZIPMTLNCKSUM', '1')
    os.environ['XRD_ZIPMTLNCKSUM'] = zip_mt_cksum
    XRD_EnvPut('ZipMtlnCksum', int(zip_mt_cksum))

    cp_retry_policy = os.getenv('XRD_CPRETRYPOLICY', 'force')
    os.environ['XRD_CPRETRYPOLICY'] = cp_retry_policy
    XRD_EnvPut('CpRetryPolicy', cp_retry_policy)


try:
    xrd_config_init()  # reset XRootD preferences to cp oriented settings - set before loading module 
    from XRootD import client as xrd_client  # type: ignore
    from XRootD.client.flags import QueryCode, OpenFlags, AccessMode, StatInfoFlags, AccessType, MkDirFlags

    XRDCP_CMD = shutil.which('xrdcp')
    HAS_XROOTD_GETDEFAULT = hasattr(xrd_client, 'EnvGetDefault')

    xrd_ver_arr = xrd_client.__version__.split(".")
    _XRDVER_1 = _XRDVER_2 = None

    if len(xrd_ver_arr) > 1:
        _XRDVER_1 = xrd_ver_arr[0][1:] if xrd_ver_arr[0].startswith('v') else xrd_ver_arr[0]  # take out the v if present
        _XRDVER_2 = xrd_ver_arr[1]
        HAS_XROOTD = int(_XRDVER_1) >= 5 and int(_XRDVER_2) > 2
    else:
        # version is not of x.y.z form, this is git based form
        xrdver_git = xrd_ver_arr[0].split("-")
        _XRDVER_1 = xrdver_git[0][1:] if xrdver_git[0].startswith('v') else xrdver_git[0]  # take out the v if present
        HAS_XROOTD = int(_XRDVER_1) > 20211113

    if not HAS_XROOTD: raise ImportError('XRootD version too low')
except Exception:
    print("XRootD module could not be imported! Not fatal, but XRootD transfers will not work (or any kind of file access)\n Make sure you can do:\npython3 -c 'from XRootD import client as xrd_client'", file = sys.stderr, flush = True)


# reset XRootD preferences to cp oriented settings - 2nd time for setting also the xrd module defaults
xrd_config_init()

class MyCopyProgressHandler(xrd_client.utils.CopyProgressHandler):
    """Custom ProgressHandler for XRootD copy process for OpenData"""
    __slots__ = ('copy_failed_list', 'jobs', 'jobs_dict', 'debug')

    def __init__(self) -> None:
        self.copy_failed_list = []  # record the failed jobs
        self.jobs = int(0)
        self.jobs_dict = {}  # dictionary to use jobId as key
        self.debug = False

    def begin(self, jobId, total, source, target) -> None:
        self.jobs = total
        JOB_INFO = {}

        # convert to str as the actual type is XRootD.client.url.URL
        JOB_INFO['src'] = str(source).replace('file://localhost', '')
        JOB_INFO['dst'] = str(target)

        timestamp_begin = datetime.datetime.now().timestamp()
        JOB_INFO['ts_begin'] = timestamp_begin

        file_stats = os.stat(JOB_INFO['src'])
        JOB_INFO['size'] = file_stats.st_size

        self.jobs_dict[jobId] = JOB_INFO
        print(f'jobID: {jobId}/{total} >>> Start')

    def end(self, jobId, results) -> None:
        res = results['status']
        if res.ok:      status = 'OK'
        elif res.error: status = 'ERROR'
        elif res.fatal: status = 'FATAL'
        else:           status = 'UNKNOWN'

        delimiter = '\n'
        if res.ok:
            deltaT = datetime.datetime.now().timestamp() - float(self.jobs_dict[jobId]['ts_begin'])
            speed = float(self.jobs_dict[jobId]['size'])/deltaT
            job_msg = f'{job_msg} >>> SPEED {GetHumanReadableSize(speed)}/s'
            delimiter = ' '

        job_msg = f"jobID: {jobId}/{self.jobs} >>> STATUS {status}{delimiter}{res.message}"
        print(job_msg)


def XrdCopy(job_list: list) -> list:
    """XRootD copy command :: the actual XRootD copy process"""
    handler = MyCopyProgressHandler()
    process = xrd_client.CopyProcess()
    process.parallel(12)  # do this number of parallel operations

    for copy_job in job_list:
        # https://github.com/xrootd/xrootd/blob/master/bindings/python/libs/client/copyprocess.py#L74
        process.add_job(copy_job[0], copy_job[1],
                        posc = True, mkdir = True, force = False,
                        retry = xrd_client.EnvGetInt('CpRetry'),
                        cptimeout = xrd_client.EnvGetInt('CPTimeout'),
                        xrateThreshold = xrd_client.EnvGetInt('XRateThreshold')
                       )

    process.prepare()
    process.run(handler)
    return handler.copy_failed_list  # lets see what failed and try to recover

