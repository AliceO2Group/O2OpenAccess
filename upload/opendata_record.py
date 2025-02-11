
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
    schema: str = "http://opendata.cern.ch/schema/records/record-v1.0.0.json"
    _bucket: str = ''
    _file_indices: list = []
    usage: dict = {
      "description": "You can access and analyse these data through the ALICE Virtual Machine. Please follow the instructions for getting started and setting up the Virtual Machine:",
      "links": [
            { "description": "Getting started with ALICE data", "url": "/getting-started/ALICE" },
            { "description": "How to install the ALICE Virtual Machine", "url": "/VM/ALICE" }
        ]
    }

class runRec(RecordClass):
    created: str = ''
    updated: str = ''
    date_created: list  = []
    date_published: str = ''
    id: str = ''
    accelerator: str = "CERN-LHC"
    collaboration: dict = { "name": "ALICE Collaboration" }
    collections: list = [ "ALICE-Reconstructed-Data" ]
    abstract: dict = { "description": "" }
    collision_information: dict = { "energy": "", "type": "" }
    doi: str = ''
    experiment: list = [ "ALICE" ]
    files: list = []
    license: dict = { "attribution": "CC0" }
    publisher: str = "CERN Open Data Portal"
    recid: str = ''
    title: str = ''
    title_additional: str = ''
    type: dict = { "primary": "Dataset", "secondary": [ "Collision" ] }
    links: dict = { "bucket": "", "self": "" }
    distribution: dict = {}
    metadata: dict = {}

