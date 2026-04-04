import boto3  #aws ka python SDK
from src.configuration.aws_connection import S3Client
from io import StringIO   #memory based file object--> csv ko dataframe banaane ke liye
from typing import Union, List
import os, sys
from src.logger import logging
from mypy_boto3_s3.service_resource import Bucket
from src.exception import MyException
from botocore.exceptions import ClientError  #to handle aws errors
import pickle
from pandas import DataFrame, read_csv


#ye class basically ek s3 helper h--> becomes pipeline ka aws interface
class SimpleStorageService:
    """
    A class for interacting with AWS S3 storage, providing methods for file management, 
    data uploads, and data retrieval in S3 buckets.
    """

    def __init__(self):
        """
        Initializes the SimpleStorageService instance with S3 resource and client
        from the S3Client class.
        """
        s3_client = S3Client()  #we call our s3client to form the aws connection 
        self.s3_resource = s3_client.s3_resource   #s3client k class k s3_resource ko self meh initialize krde rahe hai
        self.s3_client = s3_client.s3_client
#resource se humlog high level kaam kar sakte hai like bucket bulana, ec2 trigger karna, etc etc
#client se humlog low level kaam kar sakte hai jaise ki uss bucket meh kuch daalna ya nikaalna


#s3 meh key path matlab file path--> toh we are checking ki kya ye file exist karti hai ya nahi by prefix matching
    def s3_key_path_available(self, bucket_name, s3_key) -> bool:
        """
        Checks if a specified S3 key path (file path) is available in the specified bucket.

        Args:
            bucket_name (str): Name of the S3 bucket.
            s3_key (str): Key path of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        try:
            bucket = self.get_bucket(bucket_name)
            file_objects = [file_object for file_object in bucket.objects.filter(Prefix=s3_key)]  #jo humne key path input kiya h uske prefix se filter out kr rahe hai simply
            return len(file_objects) > 0  #returns boolean true or false
        except Exception as e:
            raise MyException(e, sys)

#Note: static methods are created when a function does not require instance variables and just needs input
    @staticmethod
    def read_object(
        object_name: str, decode: bool = True, make_readable: bool = False
    ) -> Union[StringIO, str, bytes]:
        """
        Reads the specified S3 object with optional decoding and formatting.

        Args:
            object_name: S3 ObjectSummary (has .get()).
            decode: If True, decode body as UTF-8 text; if False, return raw bytes (e.g. pickle).
            make_readable: If True, wrap decoded text in StringIO for pandas read_csv.

        Returns:
            StringIO (CSV path), str (decoded text), or bytes (pickle / binary).
        """
        try:
            raw: bytes = object_name.get()["Body"].read()
            if decode:
                text = raw.decode()
                if make_readable:
                    return StringIO(text)
                return text
            # decode=False: never pass bytes to StringIO (pickle.loads needs bytes)
            if make_readable:
                return StringIO(raw.decode())
            return raw
        except Exception as e:
            raise MyException(e, sys) from e
#decode = True rehta hai for csv files, qki csv binary se decode() hoga-->str(text) banega, vaha se stringIO usko wrap krke pandas read kr payega 
# model ko load krte time decode = False rehta hai because pickle.load() can only accept bytes values   


    
    def get_bucket(self, bucket_name: str) -> Bucket:
        """
        Retrieves the s3 bucket object based on the provided bucket name.

        Args:
            bucket_name (str): The name of the S3 bucket.

        Returns:
            Bucket: S3 bucket object.
        """
        logging.info("Entered the get_bucket method of the SimpleStorage class")
        try:
            bucket = self.s3_resource.Bucket(bucket_name)  #creates boto3 bucket object
            logging.info("Exited the get_bucket method of the SimpleStorage class")
            return bucket  #returns bucket obj(now any method can work inside this bucket)
        except Exception as e:
            raise MyException(e, sys) from e

        
    def get_file_object(self, filename: str, bucket_name: str) -> Union[List[object], object]:  #union matlab ya ek object ya list of objs
        """
        Retrieves the file object(s) from the specified bucket based on the filename.

        Args:
            filename (str): The name of the file to retrieve.
            bucket_name (str): The name of the S3 bucket.

        Returns:
            Union[List[object], object]: The S3 file object or list of file objects.
        """
        logging.info("Entered the get_file_object method of the SimpleStorage class")
        try:
            bucket = self.get_bucket(bucket_name)
            file_objects = [file_object for file_object in bucket.objects.filter(Prefix = filename)]
            func = lambda x: x[0] if len(x) == 1 else x  #return one file if u find only one, if multiple, return list
            file_objs = func(file_objects)  #uppar ka lambda function apply kr rahe hai file_objects meh
            logging.info("Exited the get_file_object method of the SimpleStorage class")
            return file_objs  #returns either a s3 object or a list of s3 objects
        except Exception as e:
            raise MyException(e, sys) from e
    

        
    def load_model(self, model_name: str, bucket_name: str, model_dir: str = None) -> object:
        """
        Loads a serialized model from the specified S3 bucket.

        Args:
            model_name (str): Name of the model file in the bucket.
            bucket_name (str): Name of the S3 bucket.
            model_dir (str): Optional Directory path within the bucket.

        Returns:
            object: The deserialized model object.
        """
        try:
            model_file = model_dir + "/" + model_name if model_dir else model_name
            file_object = self.get_file_object(model_file, bucket_name)
            model_obj = self.read_object(file_object, decode = False)
            model = pickle.loads(model_obj)
            logging.info("Production model loaded from s3 bucket")
            return model
        except Exception as e:
            raise MyException(e, sys) from e

        
    def create_folder(self, folder_name: str, bucket_name: str) -> None:
        """
        Creates a folder in the specified S3 bucket.

        Args:
            folder_name (str): Name of the folder to create.
            bucket_name (str): Name of the S3 bucket.
        """
        logging.info("Entered the create_folder method of the SimpleStorageService class")
        try:
            #check if folder exists by attempting to load it
            self.s3_resource.Object(bucket_name, folder_name).load()
        except ClientError as e:
            #if folder does not exist, create it
            if e.response["Error"]["Code"] == "404":
                folder_obj = folder_name + "/"
                self.s3_client.put_object(bucket = bucket_name, Key = folder_obj)
            logging.info("Exited the create_folder method of SimpleStorageService class")


    def upload_file(self, from_filename: str, to_filename: str, bucket_name: str, remove: bool = True):
        """
        Uploads a local file to the specified S3 bucket with an optional file deletion.

        Args:
            from_filename (str): Path of the local file.
            to_filename (str): Target file path in the bucket.
            bucket_name (str): Name of the S3 bucket.
            remove (bool): If True, deletes the local file after upload.
        """
        logging.info("Entered the upload_file method of the SimpleStorageService class")
        try:
            logging.info(f"Uploading {from_filename} to {to_filename} in {bucket_name}")
            self.s3_resource.meta.client.upload_file(from_filename, bucket_name, to_filename)
            logging.info(f"Uploading {from_filename} to {to_filename} in {bucket_name} completed")

        #delete the local file if remove is True
            if remove:
                os.remove(from_filename)
                logging.info(f"Removed local file {from_filename} after upload")
            logging.info("Exited the upload_file method of the SimpleStorageService class")
        except Exception as e:
            raise MyException(e, sys) from e

        
    def upload_df_as_csv(self, data_frame: DataFrame, local_filename: str, bucket_filename: str, bucket_name: str) -> None:
        """
        Uploads a DataFrame as a CSV file to the specified S3 bucket.

        Args:
            data_frame (DataFrame): DataFrame to be uploaded.
            local_filename (str): Temporary local filename for the DataFrame.
            bucket_filename (str): Target filename in the bucket.
            bucket_name (str): Name of the S3 bucket.
        """
        logging.info("Entered the upload_df_as_csv method of the SimpleStorageService class")
        try:
            data_frame.to_csv(local_filename, index = None, header = True)  
            self.upload_file(local_filname, bucket_filename, bucket_name)
            logging.info("Exited the upload_df_as_csv method of SimpleStorageService class")
        except Exception as e:
            raise MyException(e, sys) from e

        
    def get_df_from_object(self, object_: object) -> DataFrame:
        """
        Converts an S3 object to a DataFrame.

        Args:
            object_ (object): The S3 object.

        Returns:
            DataFrame: DataFrame created from the object content.
        """
        logging.info("Entered the get_df_from_object method of the SimpleStorageService class")
        try:
            content = self.read_object(object_, make_readable = True)
            df = read_csv(content)
            logging.info("Exited the get_df_from_object method of SimpleStorageService class")
            return df 
        except Exception as e:
            raise MyException(e, sys) from e

    
    def read_csv(self, filename: str, bucket_name: str) -> DataFrame:
        """
        Reads a CSV file from the specified S3 bucket and converts it to a DataFrame.

        Args:
            filename (str): The name of the file in the bucket.
            bucket_name (str): The name of the S3 bucket.

        Returns:
            DataFrame: DataFrame created from the CSV file.
        """
        logging.info("Entered the read_csv method of the SimpleStorageService class")
        try:
            csv_obj = self.get_file_object(filename, bucket_name)
            df = self.get_df_from_object(csv_obj)
            logging.info("Exited the read_csv method of SimpleStorageService class")
            return df
        except Exception as e:
            raise MyException(e, sys) from e

    
