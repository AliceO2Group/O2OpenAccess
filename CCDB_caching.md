# CCDB caching

Info from [AliceO2](https://github.com/AliceO2Group/AliceO2/tree/dev/CCDB#local-object-caching-and-testing-feature)

## Local object caching and testing feature

A simple mechanism is offered that allows caching CCDB objects on disc. In this mode, the CcdbApi will
look if an object is already located on the disc. If not, the request is made to the server and the response automically saved locally. If yes, we just
take the local file. The feature can be activated by exporting a shell variable `export ALICEO2_CCDB_LOCALCACHE=$PWD/.ccdb` which is set to a path on the disc where objects should be put. This mechanism is useful to reduce calls to the server in case multiple processes need the same objects (and the object can be regarded as valid for all requests).

Note that this mechanism also allows for local development and test cycles. Say, some algorithm needs access to object `/Foo/Bar/`.
Then it suffices to put the ROOT file containing the ccdb-object as filename `snapshot.root` inside the `/Foo/Bar/` directory structure, inside the `ALICEO2_CCDB_LOCALCACHE` folder (so, something like `/home/user/.ccdb/Foo/Bar/snapshot.root`).
Then testing can proceed without actually having to upload the CCDB object to a server.


[Command line tools](https://github.com/AliceO2Group/AliceO2/blob/dev/CCDB/README.md#command-line-tools)

## Command line tools

A few prototypic command line tools are offered. These can be used in scriptable generic workflows
and facilitate the following tasks:

  1. Upload and annotate a generic C++ object serialized in a ROOT file

     ```bash
     o2-ccdb-upload -f myRootFile.root --key histogram1 --path /Detector1/QA/ --meta "Description=Foo;Author=Person1;Uploader=Person2"
     ```
     This will upload the object serialized in `myRootFile.root` under the key `histogram1`. Object will be put to the CCDB path `/Detector1/QA`.
     For full list of options see `o2-ccdb-upload --help`.

  2. Download a CCDB object to a local ROOT file (including its meta information)

     ```bash
     o2-ccdb-downloadccdbfile --path /Detector1/QA/ --dest /tmp/CCDB --timestamp xxx
     ```
     This will download the CCDB object under path given by `--path` to a directory given by `--dest` on the disc.
     (The final filename will be `/tmp/CCDB/Detector1/QA/snapshot.root` for the moment).
     All meta-information as well as the information associated to this query will be appended to the file.

     For full list of options see `o2-ccdb-downloadccdbfile --help`.

  3. Inspect the content of a ROOT file and print summary about type of contained (CCDB) objects and its meta information

     ```bash
     o2-ccdb-inspectccdbfile filename
     ```
     Lists all keys and stored types in a ROOT file (downloaded with tool `o2-ccdb-downloadccdbfile`) and prints a summary about the attached meta-information.


## CCDB mirror

`alien.py ccdb -mirror` enable possibility to mirror a given selection content on disk.
The on-disk format respects CCDB reference and can be served by a java based http server: [ccdb-local](https://gitlab.cern.ch/grigoras/ccdb-local)
After the server is started, the configured endpoint should be used as CCDB server name.

