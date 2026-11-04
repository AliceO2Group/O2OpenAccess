#!/usr/bin/env python3

import argparse
import os
import sys
from urllib.parse import urlparse
from rich.pretty import pprint

parser = argparse.ArgumentParser(description = 'Extract CCDB paths accessed from analysis log file')
parser.add_argument('log_file', help = 'log file to be searched for read CCDB paths')
parser.add_argument('-rawpath', action = 'store_true', help = 'print the raw (full URL) paths instead of the clean paths')
args = parser.parse_args()

URL_LIST = []
with open(args.log_file, encoding="ascii", errors="replace") as filecontent:
    for line in filecontent:
        [URL_LIST.append(x) for x in line.split() if 'ccdb reads' in line and x.startswith('http:')]

PATH_LIST = []
for ccdb in URL_LIST:
    path = urlparse(ccdb).path
    path_elements = path.split('/')
    del path_elements[-2:]
    path_clean = '/'.join(path_elements)
    PATH_LIST.append(path_clean)

PATH_LIST_UNIQ = sorted(set(PATH_LIST))
PATH_LIST_UNIQ_RAW = sorted(set(URL_LIST))

if args.rawpath:
    for p in PATH_LIST_UNIQ_RAW: print(p)
else:
    for p in PATH_LIST_UNIQ: print(p)
