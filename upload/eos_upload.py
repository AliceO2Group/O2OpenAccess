#!/usr/bin/env python3

###############################
###   STEERING VARIABLES

DO_INDEX_JSON = True
DO_UPLOAD_FILES = True
DO_MAKE_RECORD = True

# RUN INFORMATION
YEAR = '2010'
PERIOD_LETTER = 'h'
RUN_NR = '139510'  # Just run number without 000 prefix

# Directory chain of the data; it will/can depend on analysis processing pass, type, other tags
# it is the part of data path the uniquely specify the data files
SPEC_DIR = '/pass3/PWGZZ/Run3_Conversion/522_20241231-1726'

# LOCAL directory where data is already downloaded; it's a prefix for actual AliEn LFN
LOCAL_BASE_DIR = '/data3'

###############################

import datetime
import sys
import os
import glob
from typing import Any, Optional, Union
import zlib
import json
import ROOT

import recordclass
from rich.pretty import pprint

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from opendata_xrd import *
from opendata_record import *
from opendata_tools import *

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

########################################
##   REQUIRED INITIAILZATION
# Enable and setup logging
setup_logging()  # type: ignore
# Create connection to JAliEn services
wb = InitConnection(cmdlist_func = constructCmdList)  # type: ignore
##   END OF INITIALIZATION
########################################

### VARIABLES DEFINITIONS

RUN = f'000{RUN_NR}'
PERIOD = f'LHC{YEAR[-2:]}{PERIOD_LETTER}'

EOSALICE = '/eos/opendata/alice'  # base directory on eospublic

EOSALICE_UPLOAD = f'{EOSALICE}/upload'     # upload directory on eospublic

EOS = 'root://eospublic.cern.ch/'  # xrootd name of server

BASE = '/alice/data'  # root directory of data files

NOW = datetime.datetime.now().isoformat()

# Mapping of run tag string to period name
PERIOD2TAG = { 'LHC10h': 'PbPb_2.76TeV', 'LHC10b': 'pp_2.76TeV', 'LHC10c': 'pp_2.76TeV', 'LHC10d': 'pp_2.76TeV', 'LHC10e': 'pp_2.76TeV',
               'LHC13b': 'pPb_2.76TeV',  'LHC13c': 'pPb_2.76TeV' }

FULL_RUN_DIR = f'{BASE}/{YEAR}/{PERIOD}/{RUN}{SPEC_DIR}'
print(f'FULL_RUN_DIR: {FULL_RUN_DIR}')

######################################################

# find details for json creation for the given RUN
ret_obj = ProcessInput(wb, 'find', ['-s', '-f', FULL_RUN_DIR, 'AO2D.root'])
find_list = ret_obj.ansdict['results']

# container for src,dst pairs to be processed by xrootd
lfn_src_dst = []
FILE_INDEX = []  # List of json dicts of files
to_delete_from_name = [SPEC_DIR, LOCAL_BASE_DIR]

for lfn_info in find_list:
    # create src,dst pair to be added to the list of uploads
    local_filepath = f'{LOCAL_BASE_DIR}{lfn_info["lfn"]}'

    eos_name2upload = lfn2eos_name(lfn_info['lfn'], to_delete_from_name, True)  # this is the upload destination
    lfn_src_dst.append((local_filepath,eos_name2upload))

    lfn_dict = {}
    lfn_dict['uri'] = lfn2eos_name(lfn_info['lfn'], to_delete_from_name, False)  # this is the actual destination, where files will be
    lfn_dict['size'] = int(lfn_info['size'])
    lfn_dict['filename'] = lfn_info['name']
    lfn_addler = adler32(local_filepath) if DO_INDEX_JSON else ''
    lfn_dict['checksum'] =  f'adler32:{lfn_addler}'
    FILE_INDEX.append(lfn_dict)


# Get number of collisions from files and assemble the collection name
COLL_NR = get_coll_list([x[0] for x in lfn_src_dst])
RUN_NAME = f'{PERIOD}_{RUN}_{PERIOD2TAG[PERIOD]}_{COLL_NR}'
print(f'RUN_NAME: {RUN_NAME}')

# Name of the index files
INDEX_JSON = f'{RUN_NAME}_file_index.json'

EOS_INDEX_DIR = f'{EOSALICE_UPLOAD}/{YEAR}/{PERIOD}/{RUN}/file-indexes'
INDEX_JSON_EOS = f'{EOS}{EOS_INDEX_DIR}/{INDEX_JSON}'

if DO_INDEX_JSON:
    # Write out the JSON index file
    FILE_INDEX_STR = json.dumps(FILE_INDEX, indent = 4) + '\n'
    with open(INDEX_JSON, 'wb') as f: f.write(FILE_INDEX_STR.encode("utf-8"))

if DO_UPLOAD_FILES:
    print('Create EOS file indexes dir')
    print(f'Creating directory for file indexes : {EOS_INDEX_DIR}')
    myxrdfs = xrd_client.FileSystem(EOS)
    status, _ = myxrdfs.mkdir(EOS_INDEX_DIR, MkDirFlags.MAKEPATH)
    print(status.message)
    print('Create EOS file indexes dir - END\n')

    print('Copy indexes')
    indexes_list = []
    indexes_list.append((os.path.abspath(INDEX_JSON), INDEX_JSON_EOS))
    result2 = XrdCopy(indexes_list)
    print('Copy indexes - END\n')

    # Upload AO2D files
    print('Copy files')
    result = XrdCopy(lfn_src_dst)
    print('Copy Files - END\n')


if DO_MAKE_RECORD:
    sum_files = int(0)
    sum_size = int(0)
    file_list = []

    for idx,f in enumerate(FILE_INDEX):
        # f_rec = fileRec()
        # f_rec.checksum = f['checksum']
        # f_rec.filename = f['filename']
        # f_rec.uri = f['uri']
        # f_rec.size = int(f['size'])
        # f_rec.key = f'{INDEX_JSON}_{idx}'
        sum_files += 1
        sum_size += int(f['size'])
        # file_list.append(recordclass.asdict(f_rec))

    ##################################################
    # file_indices = fileindexRec()
    # file_indices.files = file_list
    # file_indices.number_files = sum_files
    # file_indices.size = sum_size
    # file_indices.key = input_file_index
    # file_indices_dict = recordclass.asdict(file_indices)

    ##################################################
    # file_metadata = metadataRec()
    # file_metadata._file_indices = [ file_indices_dict ]
    # file_metadata_dict = recordclass.asdict(file_metadata)
    # file_metadata_dict['$schema'] = file_metadata_dict['schema']
    # file_metadata_dict.pop('schema')

    ##################################################
    run_record = runRec()
    # run_record.metadata = file_metadata_dict
    run_record.date_created = ['2010']
    run_record.date_published = '2025'

    run_record.created = NOW
    run_record.updated = NOW

    run_record.file = INDEX_JSON_EOS
    record_dict = recordclass.asdict(run_record)
    ##################################################

    # Write out the JSON index file
    record_file_name = INDEX_JSON.replace('_file_index.json','') + '_record.json'
    record_out = json.dumps(record_dict, indent = 4) + '\n'
    with open(record_file_name, 'wb') as f: f.write(record_out.encode("utf-8"))


