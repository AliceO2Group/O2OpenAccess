import os
import requests
import sys
import zlib
import ROOT
from typing import Optional

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


def lfn2eos_name(lfn: str, delete_tokens: Optional[list] = None, to_upload: bool = True ) -> str:
    '''Convert a local filepath to the EOSPUBLIC destination'''
    out = lfn
    EOS = 'root://eospublic.cern.ch/'
    if delete_tokens:
        for token in delete_tokens: out = out.replace(token, '')
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


def getRunInfo(runnr: str) -> dict:
    '''Return run information from Monalisa special jsp'''
    if not runnr: return {}
    url = f'http://alimonitor.cern.ch/export/opendata.jsp?run={runnr}'
    query_run = requests.get(url, timeout = 5)

    if query_run.status_code != 200:
        print(f'Invalid answer (code {query_run.status_code}) from query: {url}')
        return {}

    return query_run.json()

