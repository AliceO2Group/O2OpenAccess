#!/usr/bin/env python3

import argparse
import sys
import os
from pathlib import Path

# import alienpy functions
try:
    from alienpy.wb_api import retf_print
    from alienpy.alien import *  # nosec PYL-W0614
    import alienpy.alien as alienpy_alien
    from alienpy.tools_nowb import fileline2list
except Exception as e:
    print(f"Can't load alienpy, exiting...\n{e!r}", file = sys.stderr, flush = True)
    sys.exit(1)

parser = argparse.ArgumentParser(description = 'CCDB mirror of a list of objects for a given run')

parser.add_argument('-t', '--target', nargs = 1, required = True, help = 'Base/root directory where the mirroring will be done', dest = 'dst', metavar = 'BASE_DIR')
parser.add_argument('-r', '--runnr', nargs = 1, required = True, type = int, help = 'Run number for the CCDB objects', dest = 'runnr', metavar = 'RUN_NUMBER')
parser.add_argument('-i', '--input', nargs = 1, help = 'Input file with CCDB paths to be mirrored (one per line)', dest = 'inputf', metavar = 'INPUT_FILE')
parser.add_argument('ccdb_paths', nargs = '*', help = 'CCDB paths to be mirrored', metavar = 'CCDB_PATH')

args = parser.parse_args()

ccdb_paths = args.ccdb_paths
if args.inputf:
    if not os.path.isfile(args.inputf[0]):
        print(f'Input file >{args.inputf[0]}< not found', file = sys.stderr, flush = True)
        sys.exit(1)
    ccdb_paths.extend(fileline2list(args.inputf[0]))

if not ccdb_paths:
    print('No CCDB paths specified (use positional arguments and/or -i INPUT_FILE)', file = sys.stderr, flush = True)
    sys.exit(1)

dst_dir = os.path.realpath(args.dst[0])
if not os.path.isdir(dst_dir):
    try:
        Path(dst_dir).mkdir(parents = True, exist_ok = True)
    except Exception as e:
        print(f'{e}\nCould not create destination directory >{dst_dir}<', file = sys.stderr, flush = True)
        sys.exit(1)

runnr = str(args.runnr[0])

########################################
##   REQUIRED INITIAILZATION

# Enable and setup logging
setup_logging()  # type: ignore

# Create connection to JAliEn services
wb = InitConnection(cmdlist_func = constructCmdList)  # type: ignore
# DO_ccdb_query uses the alien.py module-level ALIENPY_GLOBAL_WB; without this it opens a second connection
alienpy_alien.ALIENPY_GLOBAL_WB = wb

##   END OF INITIALIZATION
########################################

# CCDB paths with validity in run numbers (not in ms timestamps): -run (SOR time) cannot select their objects,
# so they are always mirrored with the run number as validity time in the query
RUN_VALIDITY_PATHS = ('RCT/Info/RunInformation',)

mirror_jobs = [(path, ['-history', '-limit', '9999', '-mirror', '-dst', dst_dir, f'{path}/{runnr}']) for path in RUN_VALIDITY_PATHS]
mirror_jobs.extend((path, ['-history', '-limit', '9999', '-run', runnr, '-mirror', '-dst', dst_dir, path]) for path in ccdb_paths if path.strip('/') not in RUN_VALIDITY_PATHS)

final_exitcode = 0
for path, mirror_args in mirror_jobs:
    rez = DO_ccdb_query(mirror_args)
    exitcode = retf_print(rez)
    if exitcode != 0:
        print(f'Mirroring failed for >{path}< (exitcode {exitcode})', file = sys.stderr, flush = True)
        final_exitcode = exitcode

sys.exit(final_exitcode)
