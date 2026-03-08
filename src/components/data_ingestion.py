import os
import sys 

from pandas import DataFrame 
from sklearn.model_selection import train_test_split

from src.entity.config_entity import DataIngestionConfig
from src.entity.artifact_entity import DataIngestionArtifact 
from src.data_access.proj1_data import Proj1Data 
from src.logger import logging 
from src.exception import MyException 


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig = DataIngestionConfig()): 
        """
        :param data_ingestion_config: configuration for data ingestion
        """
        try:
            self.data_ingestion_config = data_ingestion_config #doing this so that we can access it's values in other methods
        except Exception as e:
            raise MyException(e, sys)

    def export_data_into_feature_store(self) -> DataFrame:
        """
        Method Name :   export_data_into_feature_store
        Description :   This method exports data from mongodb to csv file
        
        Output      :   data is returned as artifact of data ingestion components
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            logging.info("Exporting data from MongoDB")
            my_data = Proj1Data()
            dataframe = my_data.export_collection_as_dataframe(collection_name=self.data_ingestion_config.collection_name)
            #proj1data() ka method export_collection_as_dataframe() ko call karta hai so we can convert collection to df

            logging.info(f"Shape of dataframe: {dataframe.shape}")
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path 
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok = True)

            
            logging.info(f"Saving exported data into feature store: {feature_store_file_path}")
            dataframe.to_csv(feature_store_file_path, index = False, header = True)
            return dataframe 
        except Exception as e:
            raise MyException(e, sys)

    def split_data_as_train_test(self, dataframe: DataFrame) -> None:
        """
        Method Name :   split_data_as_train_test
        Description :   This method splits the dataframe into train set and test set based on split ratio 
        
        Output      :   Folder is created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            train_set, test_set = train_test_split(dataframe, test_size = self.data_ingestion_config.train_test_split_ratio)
            logging.info("Train test split done")

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok = True)

            logging.info("Exporting train and test data")
            train_set.to_csv(self.data_ingestion_config.training_file_path, index = False, header = True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index = False, header = True)
            logging.info("Exported train and test data")
        except Exception as e:
            raise MyException(e, sys) 


#simply calls the above two methods to initiate data ingestion
    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
        Method Name :   initiate_data_ingestion
        Description :   This method initiates the data ingestion components of training pipeline 
        
        Output      :   train set and test set are returned as the artifacts of data ingestion components
        On Failure  :   Write an exception log and then raise an exception
        """
        logging.info("Entered initiate_data_ingestion method of DataIngestion class")

        try:
            dataframe = self.export_data_into_feature_store()
            logging.info("Got the data from MongoDB")
            
            self.split_data_as_train_test(dataframe)
            logging.info("Performed train test split on the dataframe")

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path = self.data_ingestion_config.training_file_path,
                test_file_path = self.data_ingestion_config.testing_file_path,
            )
            logging.info(f"Data ingestion artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise MyException(e, sys) from e


            
