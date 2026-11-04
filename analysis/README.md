This is a basic processing workflow to be used as template

Contents

* config.json : json configuration for the basic analysis task found in this directory
* run_analysis : basic analysis task
* create_sif_from_cvmfs : create a local SIF apptainer image from a sandboxed one (from ALICE cvmfs location)
* exec_container : execute run_analysis script within a container
* exec_local : execute run_analysis script in an generated working directory (but in the context of local host operating system)
* eos_list_files : create a listing of files from EOS OpenData server taking as input an string formated like YEAR/PERIOD
* file.list : list of files to be processed (an example with a single file)
* make_env_cvmfs : create an environment file that prepare the environment for the usage of a given software stack version (cvmfs version)
* make_env_local : create an environment file that prepare the environment for the usage of a given software stack version (local version)


### Create file list of data files

Use `eos_list_files` script to create a local file list, e.g.:
```
./eos_list_files 2015/LHC15o
```

this will create 2015_LHC15o.list
