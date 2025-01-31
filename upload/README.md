


## Load O2Physics within environment

to be put in .bashrc   
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



