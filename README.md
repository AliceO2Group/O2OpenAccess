# O2openaccess
Repository for ALICE open access software

### Building

Use `./build_cmd` for task compilation
It has the following flags:
* `local` - specify to use a local build of O2Physics (the defautl tags is found in the script)
* `debug` - enable very verbose debug options for cmake
* `-tag` - specify the label mapped to packages build version

### Running

Use the provided `./run_analysis` example to run analysis in an _already_ loaded environment

### Running in singularity container

See the content of `cvmfs` directory
* `./run_cvmfs_analysis` will load a cvmfs O2Physics version and run the analysis
* `./cvmfs_cmd` will run the above script within the provided container with the help of `cvmfs2go` script


