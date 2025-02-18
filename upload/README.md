## Basic tool usage

```
./eos_upload.py -h
usage: eos_upload.py [-h] [-idx] [-up] [-rec] -basedir LOCAL_BASE_DIR -specdir SPEC_DIR runnr

ALICE OpenData tool for creation (and upload) of record json files

positional arguments:
  runnr                 Run number for which records are created

optional arguments:
  -h, --help            show this help message and exit
  -idx, --index         Enable creation of file index json file
  -up, --upload         Enable upload of file index json file
  -rec, --record        Enable creation of run record json file
  -basedir LOCAL_BASE_DIR, --basedir LOCAL_BASE_DIR
                        Specify directory where ALICE data is mirrored (full LFN path)
  -specdir SPEC_DIR, --specdir SPEC_DIR
                        Specify directory components (after run path LFN - up to AO2D directories; e.g. :
                        /pass3/PWGZZ/Run3_Conversion/522_20241231-1726)
```

## Load O2Physics within environment

If no `alienpy`/`xjalienfs` package is installed user-side and no ROOT available,   
then the ALICE software must be loaded.   

For conveninece a function to load O2Physics is to be put in .bashrc   
```
o2phys_cvmfs_load () {
local TAG CVMFS WORK_DIR ALIBUILD_ARCH_PREFIX
TAG=${1}
shift

WORK_DIR="/cvmfs/alice.cern.ch"
ALIBUILD_ARCH_PREFIX="el9-x86_64/Packages"

CVMFS="${WORK_DIR}/${ALIBUILD_ARCH_PREFIX}/O2Physics/${TAG}/etc/profile.d/init.sh"
[[ ! -f ${CVMFS} ]] && { return; }

source "${CVMFS}"
}
```

then within the current terminal:   
```
o2phys_cvmfs_load daily-20250130-0000-1
```

N.B. it cannot be unloaded! the bash session must be closed for a new environment.


## Local data

Data is supposed to be already mirrored locally.(see `download_file_list` script)   
It takes as input a file with `LFN file:/BASEDIR` pairs (1 pair per line).   
`BASEDIR` is the location where full filepath of data will be mirrored.   

## Uploading data

The access to EOS public is given based on kerberos token.   
Have a configuration file like [this one](https://github.com/adriansev/bin-scripts/blob/master/env/krb5.conf) or copy one from lxplus   
and then have within the environment `export KRB5_CONFIG="path_to_krb5.conf"`   
Then, a kerberos token can be created with: `kinit -l '25:00' -r '120:00' -fp <CERN_USERNAME>@CERN.CH`
`xrdcp` will automatically find and use the token (if no xrdgsiproxy is already created)   



