#!/usr/bin/env python3

import argparse
import sys

parser = argparse.ArgumentParser(description = 'CCDB :: get Start/Stop for run')
parser.add_argument('runnr', nargs = '+', help = 'Run number or a list of run numbers')
out_fmt = parser.add_mutually_exclusive_group()
out_fmt.add_argument('-json', help = 'JSON output of the extracted SOR/EOR information', action = 'store_true')
out_fmt.add_argument('-rawjson', help = 'JSON output of the full CCDB RunInformation answer', action = 'store_true')
args = parser.parse_args()

# import alienpy functions; alienpy.alien must be the first alienpy import (it initializes logging)
try:
    import requests
    from alienpy.alien import ccdb_runinfo
    from alienpy.tools_nowb import unixtime2local, PrintDict
except Exception as e:
    print(f"Can't load alienpy, exiting...\n{e!r}", file = sys.stderr, flush = True)
    sys.exit(1)

raw_list = []
rez_list = []
for r in args.runnr:
    try:
        run_info = ccdb_runinfo(r)
    except requests.exceptions.RequestException as e:
        print(f'CCDB query failed for {r}: {e!r}', file = sys.stderr, flush = True)
        continue
    if 'objects' not in run_info or not run_info['objects']:
        print(f'No information found for {r}', file = sys.stderr, flush = True)
        continue

    if args.rawjson:
        raw_list.append(run_info)
        continue

    obj = run_info['objects'][0]
    rez_list.append({ 'run': r,
                      'sor': obj['SOR'], 'eor': obj['EOR'],
                      'sor_nice': unixtime2local(obj['SOR']), 'eor_nice': unixtime2local(obj['EOR'])})

# results presentation
if args.rawjson:
    PrintDict(raw_list)
    sys.exit()

if args.json:
    PrintDict(rez_list)
    sys.exit()

for i in rez_list:
    print(f'run="{i["run"]}"  sor="{i["sor"]}"  eor="{i["eor"]}"  sor_nice="{i["sor_nice"]}"  eor_nice="{i["eor_nice"]}"')
