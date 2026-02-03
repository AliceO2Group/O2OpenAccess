# O2openaccess

Repository for ALICE open access software

## ALICE software documentation

https://aliceo2group.github.io/analysis-framework/  
https://indico.cern.ch/event/1267433/timetable/#20230417.detailed  

### Structure of repository

* Root of repository have the enable/enable_local and build_cmd scripts used for  
  loading O2Physics environment and build the example analysis from `src/` directory
    * These are supposed to be used/run outside of any already loaded environment
    * enable/enable_local take as a 1st argument a tag name of O2Physics installation
    * build_cmd take as argument `[local] tag_name` where `local` specify that the tag_name is of a local O2Physics installation and as such enable_local script will be used

* `cmake/` and `src/` contain the example analysis task
    * the compilation of this stand-alone analysis task is done by build_cmd command   

* `analysis/` directory contain the files required to run an example analysis
    * see the `analysis/README.md`

* `container/` have the tools to build an cvmfs enabled EL9 container

* `cvmfs/` have `cvmfs2go` script to be able to use cvmfs within a container (for hosts where cvmfs is not available)
    * taken from https://github.com/adriansev/cvmfs2go
    * see the `cvmfs/README.md` for more information

* `upload/` have the tools to upload data to OpenData EOS storage


### Environment setup

The environment (the package dependencies and the package path) is setup by running:  

* For usage of cvmfs distributed O2Physics: `source enable <optional O2Physics tag>`  
* For usage of a local compiled O2Physics: `source enable_local <optional O2Physics local build tag>`  

There are a few of steering env vars:  
O2OPENACCESS_SW_TAG_LOCAL : tag name to be used for O2Physics dependency(local installed); It has a default of: latest-o2physics-o2  

O2OPENACCESS_SW_TAG_CVMFS : tag name to be used for O2Physics dependency(cvmfs based); It has a default of: daily-20260126-0000-1  

### Building

Within the repository, use `./build_cmd` for task compilation
It has the following flags:

* `debug` : enable very verbose debug options for cmake
* `enable`/`enable_local` take as a 1st argument a tag name of O2Physics installation
* `build_cmd` take as argument `[local] tag_name` where `local` specify that the tag_name is of a local O2Physics installation and as such `enable_local` script will be used

### Running

Use the provided `./run_analysis` example to run analysis in an _already_ loaded environment

To find help on options use:
`o2-analysistutorial-flow-analysis --help`

or for more comprehensive help
`o2-analysistutorial-flow-analysis --help full`

### Running in singularity container

See the content of `cvmfs` directory for a custom container and content of `analysis/README.md`

