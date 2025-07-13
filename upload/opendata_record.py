
import sys
from recordclass import RecordClass

class fileRec(RecordClass):
    bucket: str = ''
    checksum: str = ''
    file_id: str = ''
    filename:str = 'AO2D.root'
    key: str = ''
    size: int = 0
    uri: str = ''
    version_id: str = ''

class distributionRec(RecordClass):
    formats: list = [ "root" ]
    number_events: int = 0
    number_files: int = 0
    size: int = 0

class fileindexRec(RecordClass):
    files: list = []
    key: str = ''
    number_files: int = 0
    size: int = 0

class metadataRec(RecordClass):
#    schema: str = "http://opendata.cern.ch/schema/records/record-v1.0.0.json"
#    _bucket: str = ''
#    _file_indices: list = []
    usage: dict = {
      "description": "Follow information from https://github.com/AliceO2Group/O2OpenAccess to access and analyse these data",
      "links": [
            { "description": "Getting started with ALICE data analysis", "url": "https://aliceo2group.github.io/analysis-framework/" },
            { "description": "Use O2OpenAccess demonstrator", "url": "https://github.com/AliceO2Group/O2OpenAccess" }
        ]
    }


class runRec(RecordClass):
    abstract: dict = { "description": "" }
    accelerator: str = "CERN-LHC"
    collaboration: dict = { "name": "ALICE Collaboration" }
    collections: list = [ "ALICE-Reconstructed-Data" ]
    collision_information: dict = { "energy": "", "type": "" }
    created: str = ''
    date_created: list  = []
    date_published: str = ''
    distribution: dict = {}
    experiment: list = [ "ALICE" ]
    files: list = []
    license: dict = { "attribution": "CC0-1.0" }
    publisher: str = "CERN Open Data Portal"
    recid: str = ''
    title: str = ''
    title_additional: str = ''
    type: dict = { "primary": "Dataset", "secondary": [ "Collision" ] }
    usage: dict = {}
    keywords: list = []

