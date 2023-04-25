# O2openaccess
Repository for ALICE open access software

## ALICE software documentation
https://aliceo2group.github.io/analysis-framework/  
https://indico.cern.ch/event/1267433/timetable/#20230417.detailed  


### Environment setup

The environment (the package dependencies and the package path) is setup by running:  
`source enable`  

There are a few of steering env vars:  
O2OPENACCESS_USE_LOCAL : set to any value to use the user-defined local tag or the default one (see below)  

O2OPENACCESS_SW_TAG_LOCAL : tag name to be used for O2Physics dependency(local installed); It has a default of: latest-o2physics-o2  

O2OPENACCESS_SW_TAG_CVMFS : tag name to be used for O2Physics dependency(cvmfs based); It has a default of: nightly-20230423-1  

The default behaviour is that O2OPENACCESS_USE_LOCAL is not set, and cvmfs dependency will be used  


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


