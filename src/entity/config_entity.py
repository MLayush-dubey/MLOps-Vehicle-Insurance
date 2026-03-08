#input configurations

import os
from src.constants import *
from dataclasses import dataclass
from datetime import datetime

TIMESTAMP: str = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

"""
Dataclass ka main purpose hai:
- Data class se we can create classes without any constructor.
- Structured data ko clean aur readable way me store karna.
"""
@dataclass
class TrainingPipelineConfig:
    pipeline_name: str = PIPELINE_NAME
    artifact_dir: str = os.path.join(ARTIFACT_DIR, TIMESTAMP)
    timestamp: str = TIMESTAMP


training_pipeline_config: TrainingPipelineConfig = TrainingPipelineConfig()

@dataclass
class DataIngestionConfig:  #configuration values-->configured in constants.py
    data_ingestion_dir: str = os.path.join(training_pipeline_config.artifact_dir, DATA_INGESTION_DIR_NAME)  # Where to save raw data
    feature_store_file_path: str = os.path.join(data_ingestion_dir, DATA_INGESTION_FEATURE_STORE_DIR, FILE_NAME)   # Full CSV path
    training_file_path: str = os.path.join(data_ingestion_dir, DATA_INGESTION_INGESTED_DIR, TRAIN_FILE_NAME)  # Train CSV
    testing_file_path: str = os.path.join(data_ingestion_dir, DATA_INGESTION_INGESTED_DIR, TEST_FILE_NAME)  # Test CSV
    train_test_split_ratio: float = DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO   #0.25
    collection_name:str = DATA_INGESTION_COLLECTION_NAME    #"Proj1-Data"
#This method of TrainPipeline class is responsible for starting data ingestion component