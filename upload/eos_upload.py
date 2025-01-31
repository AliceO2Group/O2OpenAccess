#!/usr/bin/env python3

import sys
import os
import glob
from typing import Any, Optional, Union
import zlib
import json
import ROOT

# import alienpy functions
try:
    from alienpy.wb_api import PrintDict, retf_print
    from alienpy.alien import *  # nosec PYL-W0614
except Exception:
    try:
        from xjalienfs.wb_api import PrintDict, retf_print
        from xjalienfs.alien import *  # nosec PYL-W0614
    except Exception:
        print("Can't load alienpy, exiting...")
        sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from opendata_xrd import *

from rich.pretty import pprint

###############################
###   STEERING VARIABLES

# in from most volatile to fixed ones

# RUN INFORMATION
RUN_NR = '139510'
RUN = f'000{RUN_NR}'

YEAR = '2010'
PERIOD_LETTER = 'h'

PERIOD = f'LHC{YEAR[-2:]}{PERIOD_LETTER}'

# Directory chain of the data; it will/can depend on analysis processing pass, type, other tags
SPEC_DIR = '/pass3/PWGZZ/Run3_Conversion/522_20241231-1726'

# LOCAL directory where data is already downloaded; it's a prefix for actual AliEn LFN
LOCAL_BASE_DIR = '/data3'

# Mapping of run tag string to period name
PERIOD2TAG = { 'LHC10h': 'PbPb_2.76TeV', 'LHC10b': 'pp_2.76TeV', 'LHC10c': 'pp_2.76TeV', 'LHC10d': 'pp_2.76TeV', 'LHC10e': 'pp_2.76TeV',
               'LHC13b': 'pPb_2.76TeV',  'LHC13c': 'pPb_2.76TeV' }

EOSALICE = '/eos/opendata/alice'  # base directory on eospublic
UPLOAD = f'{EOSALICE}/upload'     # upload directory on eospublic
EOS = 'root://eospublic.cern.ch'  # xrootd name of server

BASE = '/alice/data'  # root directory of data files

FULL_RUN_DIR = f'{BASE}/{YEAR}/{PERIOD}/{RUN}{SPEC_DIR}'
print(f'FULL_RUN_DIR: {FULL_RUN_DIR}')

######################################################
###   TOOLING - FUNCTIONS

def get_df_list(tfile: ROOT.TFile) -> list:
    '''Get list of DF_ prefixed directories in a TFile'''
    if not tfile: return []
    out_list = []
    for tdir in tfile.GetListOfKeys():  # for each directory
        if not tdir.IsFolder(): continue
        dir_name = tdir.GetName()
        if not dir_name.startswith('DF_'): continue
        out_list.append(dir_name)
    return out_list


def get_coll_trees(tfile: ROOT.TFile, dir_name):
    '''Get list of TTree with names prefixed by O2collision'''
    if not tfile: return []
    out_list = []
    for t in tfile.Get(dir_name).GetListOfKeys():  # get the name of the other trees from the same TDir
        if t.GetClassName() != 'TTree': continue
        name = t.GetName()
        if name.startswith('O2collision'): out_list.append(name)
    return out_list


def get_coll_nr(fname: str) -> int:
    '''Get sum of GetEntries of all DF_*/O2collision*'''
    if not fname: return 0
    if not os.path.exists(fname): return 0

    COLLS_NR = 0
    f = ROOT.TFile.Open(fname)
    if f.IsZombie():
        print(f'File is zombie: {ao2d}')
        return 0

    for df in get_df_list(f):
        colls_name = get_coll_trees(f, df)
        for coll in colls_name:
            coll_ttree = f[f'{df}/{coll}']
            COLLS_NR += coll_ttree.GetEntries()
    return COLLS_NR


def get_coll_list(file_list: list) -> int:
    '''Get a sum of all collisions in a list of files'''
    coll_nr = 0
    for f in file_list:
        if not os.path.exists(f): continue
        coll_nr += get_coll_nr(f)
    return coll_nr


def lfn2eos_name(lfn: str, to_upload: bool = True ) -> str:
    '''Convert a local filepath to the EOSPUBLIC destination'''
    out = lfn.replace(SPEC_DIR, '')
    out = out.replace(LOCAL_BASE_DIR, '')
    if to_upload:
        out = out.replace('/alice/data', '/eos/opendata/alice/upload')
    else:
        out = out.replace('/alice/data', '/eos/opendata/alice')
    return f'{EOS}/{out}'


def adler32(fname: str) -> int:
    '''Compute adler32 crc for a file'''
    if not fname: return 0
    if not os.path.exists(fname): return 0
    BLOCKSIZE = 65536
    START = None
    with open(fname, 'rb', buffering = 0) as f:
        for chunk in iter(lambda: f.read(BLOCKSIZE), b''):
            START = zlib.adler32(chunk, START) if START else zlib.adler32(chunk)
    return f'{START:x}'

######################################################
########################################
##   REQUIRED INITIAILZATION
# Enable and setup logging
setup_logging()  # type: ignore
# Create connection to JAliEn services
wb = InitConnection(cmdlist_func = constructCmdList)  # type: ignore
##   END OF INITIALIZATION
########################################

## for xml generation 
## ret_obj = ProcessInput(wb, 'find', ['-s', '-x', '-', FULL_RUN_DIR, 'AO2D.root'])
## XML_FNAME = f'{PERIOD}_{RUN}_{PERIOD2TAG[PERIOD]}_{COLL_NR}.xml'
## with open(XML_FNAME, 'w', encoding="ascii", errors="replace") as f: f.write(ret_obj.ansdict['results'][-1]['message'])

# find details for json creation for the given RUN
ret_obj = ProcessInput(wb, 'find', ['-s', '-f', FULL_RUN_DIR, 'AO2D.root'])
find_list = ret_obj.ansdict['results']

# container for src,dst pairs to be processed by xrootd
lfn_src_dst = []

FILE_INDEX = []  # List of json dicts of files
for lfn_info in find_list:
    # create src,dst pair to be added to the list of uploads
    local_filepath = f'{LOCAL_BASE_DIR}{lfn_info["lfn"]}'
    eos_name = lfn2eos_name(lfn_info['lfn'], True)
    lfn_src_dst.append((local_filepath,eos_name))

    lfn_dict = {}
    lfn_dict['uri'] = eos_name
    lfn_dict['size'] = lfn_info['size']
    lfn_dict['filename'] = lfn_info['name']
    lfn_addler = adler32(local_filepath)
    lfn_dict['checksum'] =  f'adler32:{lfn_addler}'
    FILE_INDEX.append(lfn_dict)


# Get number of collisions from files and assemble the collection name
COLL_NR = get_coll_list([x[0] for x in lfn_src_dst])
RUN_NAME = f'{PERIOD}_{RUN}_{PERIOD2TAG[PERIOD]}_{COLL_NR}'
print(f'RUN_NAME: {RUN_NAME}')

# Name of the index files
INDEX_JSON = f'{RUN_NAME}_file_index.json'
INDEX_TXT = f'{RUN_NAME}_file_index.txt'

# Write out the JSON index file
JSON_OUT = json.dumps(FILE_INDEX, indent = 4) + '\n'
with open(INDEX_JSON, 'wb') as f: f.write(JSON_OUT.encode("utf-8"))

# Write out the TXT index file
uri_eos_list = '\n'.join([x['uri'] for x in FILE_INDEX]) + '\n'
with open(INDEX_TXT, 'wb') as f: f.write(uri_eos_list.encode("utf-8"))

##################################
# Upload AO2D files
print('Copy files')
result = XrdCopy(lfn_src_dst)
print('Copy Files - END\n')


print('Create EOS file indexes dir')
EOS_INDEX_DIR = f'{EOSALICE}/upload/{YEAR}/{PERIOD}/{RUN}/file-indexes'
print(f'Creating directory for file indexes : {EOS_INDEX_DIR}')
myxrdfs = xrd_client.FileSystem(EOS)
status, _ = myxrdfs.mkdir(EOS_INDEX_DIR, MkDirFlags.MAKEPATH)
print(status.message)
print('Create EOS file indexes dir - END\n')


print('Copy indexes')
indexes_list = []
indexes_list.append((os.path.abspath(INDEX_JSON), f'{EOS}{EOS_INDEX_DIR}/{INDEX_JSON}'))
indexes_list.append((os.path.abspath(INDEX_TXT),  f'{EOS}{EOS_INDEX_DIR}/{INDEX_TXT}'))
result2 = XrdCopy(indexes_list)
print('Copy indexes - END\n')


