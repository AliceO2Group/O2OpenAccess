# O2openaccess
Repository for ALICE open access software

## ALICE software documentation
https://aliceo2group.github.io/analysis-framework/  
https://indico.cern.ch/event/1267433/timetable/#20230417.detailed  

### Structure of repository

* Root of repository have the enable/enable_local and build_cmd scripts used for  
  loading O2Physics environment and build the example analysis from `src/` directory

* `analysis/` directory contain the files required to run the exampla analysis

* `cmake/` and `src/` contain the example analysis task

* `container/` have the tools to build an cvmfs enabled EL9 container

* `cvmfs/` have the tools to use a cvmfs enabled container

* `upload/` have the tools to upload data to OpenData EOS storage

### Environment setup

The environment (the package dependencies and the package path) is setup by running:  
* For usage of cvmfs distributed O2Physics: `source enable`  
* For usage of a local compiled O2Physics: `source enable_local`  

There are a few of steering env vars:  
O2OPENACCESS_SW_TAG_LOCAL : tag name to be used for O2Physics dependency(local installed); It has a default of: latest-o2physics-o2  

O2OPENACCESS_SW_TAG_CVMFS : tag name to be used for O2Physics dependency(cvmfs based); It has a default of: daily-20251023-0000-1  


### Building

Use `./build_cmd` for task compilation
It has the following flags:
* `debug` - enable very verbose debug options for cmake

The build script make use of `enable` env setup script described above.


### Running

Use the provided `./run_analysis` example to run analysis in an _already_ loaded environment

To find help on options use:
`o2-analysistutorial-flow-analysis --help`

or for more comprehensive help
`o2-analysistutorial-flow-analysis --help full`


### Running in singularity container

See the content of `cvmfs` directory
* `./run_cvmfs_analysis` will load a cvmfs O2Physics version and run the analysis
* `./cvmfs_cmd` will run the above script within the provided container with the help of `cvmfs2go` script


