from src.cloud_storage.aws_storage import SimpleStorageService
from src.entity.estimator import MyModel
from src.exception import MyException 
from src.logger import logging
import sys 
from pandas import DataFrame 


class Proj1Estimator:
    """
    This class is used to save and retrieve our model from s3 bucket to do prediction
    """

    def __init__(self, bucket_name, model_path):
        """
        :param bucket_name: Name of your model bucket
        :param model_path: Location of your model in bucket
        """
        self.bucket_name = bucket_name 
        self.model_path = model_path 
        self.s3 = SimpleStorageService() 
        self.loaded_model:MyModel=None  #this is just for caching(ek baar model load hogaya toh usko baar baar load krne ki zarurat h)



    def is_model_present(self, model_path):
        try:
            return self.s3.s3_key_path_available(bucket_name = self.bucket_name, s3_key = model_path)
        except Exception as e:
            print(e)
            return False 
        

    def load_model(self,) -> MyModel:
        """
        Load the model from the model_path
        :return:
        """
        return self.s3.load_model(model_name = self.model_path, bucket_name = self.bucket_name)
    

    def save_model(self, from_file, remove:bool = False) -> None:
        """
        Save the model to the model_path
        :param from_file: Your local system model path
        :param remove: By default it is false that mean you will have your model locally available in your system folder
        :return:
        """
        try:
            self.s3.upload_file(from_file,
                                to_filename = self.model_path,
                                bucket_name = self.bucket_name,
                                remove = remove)
            
        except Exception as e:
            raise MyException(e, sys)
        


    def predict(self, dataframe: DataFrame):
        """
        :param dataframe:
        :return:
        """
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe = dataframe)
        
        except Exception as e:
            raise MyException(e, sys)