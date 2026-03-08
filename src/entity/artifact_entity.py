from dataclasses import dataclass

"""
The output of one component becomes the input of the next. 
Artifacts are the "handshake" between pipeline stages. 
DataIngestion produces a DataIngestionArtifact → DataValidation receives it.
"""
@dataclass
class DataIngestionArtifact:
    trained_file_path:str 
    test_file_path:str