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


@dataclass
class DataTransformationArtifact:
    transformed_object_file_path: str
    transformed_train_file_path: str
    transformed_test_file_path: str


@dataclass
class ClassificationMetricArtifact:
    f1_score: float
    precision_score: float
    recall_score: float


@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    metric_artifact: ClassificationMetricArtifact   #output meh metrics bhi aayenge issike vajah se
#the next stage which is evaluation will require trained model and metrics

