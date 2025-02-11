#!/usr/bin/env python3

import sys
import os
import glob
from typing import Any, Optional, Union
import zlib
import json
import recordclass
from datetime import datetime
from rich.pretty import pprint

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from opendata_record import *

input_file_index = 'LHC10h_000139510_PbPb_2.76TeV_205656_file_index.json'

fidx_list = {}
try:
    # Open and read the JSON file
    with open(input_file_index, 'r') as f: fidx_list = json.load(f)
except Exception as e:
    print(f'Could not load {input_file_index}\n{e}')
    sys.exit(1)

##################################################
sum_files = int(0)
sum_size = int(0)
file_list = []
for idx,f in enumerate(fidx_list):
    f_rec = fileRec()
    f_rec.checksum = f['checksum']
    f_rec.filename = f['filename']
    f_rec.uri = f['uri']
    f_rec.size = int(f['size'])
    f_rec.key = f'{input_file_index}_{idx}'
    sum_files += 1
    sum_size += int(f_rec.size)
    file_list.append(recordclass.asdict(f_rec))

##################################################
file_indices = fileindexRec()
file_indices.files = file_list
file_indices.number_files = sum_files
file_indices.size = sum_size
file_indices.key = input_file_index
file_indices_dict = recordclass.asdict(file_indices)

##################################################
file_metadata = metadataRec()
file_metadata._file_indices = [ file_indices_dict ]
file_metadata_dict = recordclass.asdict(file_metadata)
file_metadata_dict['$schema'] = file_metadata_dict['schema']
file_metadata_dict.pop('schema')

##################################################
run_record = runRec()
run_record.metadata = file_metadata_dict
run_record.date_created = ['2010']
run_record.date_published = '2025'

now = datetime.now().isoformat()
run_record.created = now
run_record.updated = now

record_dict = recordclass.asdict(run_record)
##################################################

# Write out the JSON index file
record_file_name = input_file_index.replace('_file_index.json','') + '_record.json'
record_out = json.dumps(record_dict, indent = 4) + '\n'
with open(record_file_name, 'wb') as f: f.write(record_out.encode("utf-8"))

