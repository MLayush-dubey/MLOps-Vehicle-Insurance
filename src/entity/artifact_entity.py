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

@dataclass   
class DataValidationArtifact:
    validation_status: bool 
    message: str 
    validation_report_file_path: str
#ye artifact hai jo data validation ke liye bana hai jo batayega ki output data valid hai ya nahi, 
# iska logic likhenge in components.data_validation.py file