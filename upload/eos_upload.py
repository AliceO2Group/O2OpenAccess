#!/usr/bin/env python3

import argparse
import datetime
import sys
import os
import glob
from typing import Any, Optional, Union
import zlib
import json
import ROOT

import recordclass
#from rich.pretty import pprint

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
    print("Can't load alienpy, exiting...")
    sys.exit(1)


##########################################################
###   Parse arguments
parser = argparse.ArgumentParser(description = 'ALICE OpenData tool for creation (and upload) of record json files')

parser.add_argument('-noidx', '--noindex',  required = False, action='store_false', help = 'Disable creation of file index json file; default = False', dest = 'DO_INDEX_JSON')
parser.add_argument('-up',  '--upload', required = False, action='store_true', help = 'Enable upload of file index json file; default = False', dest = 'DO_UPLOAD_FILES')
parser.add_argument('-norec', '--norecord', required = False, action='store_false', help = 'Disable creation of run record json file; default = False', dest = 'DO_MAKE_RECORD')
parser.add_argument('-basedir', '--basedir', required = True, help = 'Specify directory where ALICE data is mirrored (full LFN path)', dest = 'LOCAL_BASE_DIR')
parser.add_argument('-specdir', '--specdir', required = True, help = 'Specify directory components (after run path LFN - up to AO2D directories; e.g. : /pass3/PWGZZ/Run3_Conversion/522_20241231-1726)', dest = 'SPEC_DIR')
parser.add_argument('runnr', help = 'Run number for which records are created')
args, _ = parser.parse_known_args()

RUN_NR = args.runnr

DO_INDEX_JSON = args.DO_INDEX_JSON
DO_UPLOAD_FILES = args.DO_UPLOAD_FILES
DO_MAKE_RECORD = args.DO_MAKE_RECORD

# Directory chain of the data; it will/can depend on analysis processing pass, type, other tags
# it is the part of data path that uniquely specify the data files; e.g. /pass3/PWGZZ/Run3_Conversion/522_20241231-1726
SPEC_DIR = args.SPEC_DIR

# LOCAL directory where data is already downloaded; it's a prefix for actual AliEn LFN
LOCAL_BASE_DIR = args.LOCAL_BASE_DIR

########################################
##   REQUIRED INITIAILZATION
# Enable and setup logging
setup_logging()  # type: ignore
# Create connection to JAliEn services
wb = InitConnection(cmdlist_func = constructCmdList)  # type: ignore
##   END OF INITIALIZATION
########################################

### VARIABLES DEFINITIONS
NOW = datetime.datetime.now().isoformat()

runinfo_dict = getRunInfo(str(RUN_NR))
if not runinfo_dict:
    print(f'Could not get information about run: {RUN_NR}')

YEAR = str(runinfo_dict["year"])
PERIOD = runinfo_dict["period"]

# Get beam type and try to normalize to something consistent and sane : <Part1>-<Part2>
BEAM_TYPE = runinfo_dict["beamtype"].casefold()  # go to lowercase for easier conversions
BEAM_TYPE = BEAM_TYPE.replace(' ','').replace('82','').replace('-','')  # as per 20250209 Tibor's email
BEAM_TYPE = BEAM_TYPE.replace('proton', 'p')
BEAM_TYPE = BEAM_TYPE.replace('pb', 'Pb')

# Convert numeric enery to a nice looking string
ENERGY = round((2 * runinfo_dict["energy"])/1000., 2)
ENERGY_STR = f'{ENERGY}TeV'

TAG = f'{BEAM_TYPE}_{ENERGY_STR}'

RUN = f'000{RUN_NR}'

EOSALICE = '/eos/opendata/alice'  # base directory on eospublic

EOSALICE_UPLOAD = f'{EOSALICE}/upload'     # upload directory on eospublic

EOS = 'root://eospublic.cern.ch/'  # xrootd name of server

BASE = '/alice/data'  # root directory of data files

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
RUN_NAME = f'{PERIOD}_{RUN}_{TAG}_{COLL_NR}'

print(f'RUN_NAME: {RUN_NAME}\nBEAM_TYPE: {BEAM_TYPE}\nENERGY: {ENERGY_STR}')

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
    file_metadata = metadataRec()
    file_metadata_dict = recordclass.asdict(file_metadata)

    ##################################################
    distribution_rec = distributionRec()
    distribution_rec.number_events = COLL_NR
    distribution_rec.number_files = sum_files
    distribution_rec.size = sum_size
    distribution_rec_dict = recordclass.asdict(distribution_rec)

    ##################################################
    ### Add file Dict for index file
    f_idx_rec = {}
    f_idx_rec['type'] = 'index.json'
    f_idx_rec['uri'] = INDEX_JSON_EOS
    f_idx_rec['size'] = os.stat(INDEX_JSON).st_size
    f_idx_rec['checksum'] = f'adler32:{adler32(INDEX_JSON)}'

    ##################################################
    run_record = runRec()
    # run_record.metadata = file_metadata_dict
    run_record.date_created = [ YEAR ]
    run_record.date_published = '2025'
    run_record.title = RUN_NAME
    run_record.created = NOW
    run_record.updated = NOW
    run_record.files.append(f_idx_rec)
    run_record.usage = file_metadata_dict
    run_record.distribution = distribution_rec_dict
    run_record.collision_information = {'type': BEAM_TYPE, 'energy': ENERGY_STR}

    # Create a nice description
    BEAM_TYPE_NICE = BEAM_TYPE.replace('Pb', 'Lead').replace('p', 'Proton').replace('Xe', 'Xenon')
    BEAM_TYPE_NICE = BEAM_TYPE_NICE.replace('Proton', 'Proton-', 1).replace('Lead', 'Lead-', 1).replace('Xenon', 'Xenon-', 1)
    DESCRIPTION = f'{BEAM_TYPE_NICE} data sample at the collision energy of {ENERGY_STR} from run number {RUN_NR} of the {PERIOD} data taking period.'
    run_record.abstract = {'description': DESCRIPTION }
    run_record.title_additional = DESCRIPTION

    #run_record.file = INDEX_JSON_EOS
    record_dict = recordclass.asdict(run_record)
    ##################################################

    record2write = [ record_dict ]

    # Write out the JSON index file
    record_file_name = INDEX_JSON.replace('_file_index.json','') + '_record.json'
    record_out = json.dumps(record2write, indent = 4) + '\n'
    with open(record_file_name, 'wb') as f: f.write(record_out.encode("utf-8"))


