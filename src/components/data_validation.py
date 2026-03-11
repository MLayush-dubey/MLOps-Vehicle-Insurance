import json 
import os 
import sys 

import pandas as pd 
from pandas import DataFrame 

from src.exception import MyException 
from src.logger import logging 
from src.utils.main_utils import read_yaml_file 
from src.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact 
from src.entity.config_entity import DataValidationConfig 
from src.constants import SCHEMA_FILE_PATH 


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        """
        :param data_ingestion_artifact: Output reference of data ingestion artifact stage
        :param data_validation_config: configuration for data validation
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact 
            self.data_validation_config = data_validation_config 
        except Exception as e:
            raise MyException(e, sys) from e 
        
    
    def validate_number_of_columns(self, dataframe: DataFrame) -> bool:   #artifact_entity meh validation_status hai jo true ya false return karegi
        """
        Method Name :   validate_number_of_columns
        Description :   This method validates the number of columns
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            status = len(dataframe.columns) == self.data_validation_config.no_of_columns 
            logging.info(f"Validation status: {status}")
            return status 
        except Exception as e:
            raise MyException(e, sys) from e 
        


    def is_columns_exist(self, df: DataFrame) -> bool:
        """
        Method Name :   is_column_exist
        Description :   This method validates the existence of a numerical and categorical columns
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            dataframe_columns = df.columns 
            missing_numerical_columns = []
            missing_categorical_columns = [] 
            for column in self.data_validation_config.numerical_columns:
                if column not in dataframe_columns:
                    missing_numerical_columns.append(column)

            if len(missing_numerical_columns)>0:
                logging.info(f"Missing numerical column: {missing_numerical_columns}")

            
            for column in self.data_validation_config.categorical_columns:
                if column not in dataframe_columns:
                    missing_categorical_columns.append(column)

            if len(missing_categorical_columns)>0:
                logging.info(f"Missing categorical column: {missing_categorical_columns}")

            return False if len(missing_categorical_columns)>0 or len(missing_numerical_columns)>0 else True   #taaki pipeline yahi rukjaye
        except Exception as e:
            raise MyException(e, sys)

        

