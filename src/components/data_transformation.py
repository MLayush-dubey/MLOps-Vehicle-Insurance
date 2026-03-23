import sys
import numpy as np
import pandas as pd
from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.compose import ColumnTransformer

from src.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, CURRENT_YEAR
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact
from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import save_object, save_numpy_array_data, read_yaml_file


class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, 
                data_transformation_config: DataTransformationConfig, 
                data_validation_artifact: DataValidationArtifact):
                try:
                    self.data_ingestion_artifact = data_ingestion_artifact
                    self.data_transformation_config = data_transformation_config
                    self.data_validation_artifact = data_validation_artifact   
                    self._schema_config = read_yaml_file(file_path = SCHEMA_FILE_PATH)  #basically saare artifacts, ingestion k are loaded and then we read them
                except Exception as e:
                    raise MyException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise MyException(e, sys)


    def get_data_transformer_object(self) -> Pipeline:
        """
        Creates and returns a data transformer object for the data, 
        including gender mapping, dummy variable creation, column renaming,
        feature scaling, and type adjustments.
        """
        logging.info("Entered get_data_transformer_object method of DataTransformation class")

        try:
            #initialize transformers
            numeric_transformer = StandardScaler()
            min_max_scaler = MinMaxScaler()
            logging.info("Transformers initialized: StandardScaler-MinMaxScaler")

            #load schema configurations
            num_features = self._schema_config['num_features']  #schema.yaml meh se retrieve kr raha hai ye
            mm_columns = self._schema_config['mm_columns']
            logging.info("Cols loaded from schema")

            #create preprocesser pipeline
            preprocessor = ColumnTransformer(
                transformers = [
                    ("StandardScaler", numeric_transformer, num_features),  #standard scaler is applied to numeric features
                    ("MinMaxScaler", min_max_scaler, mm_columns)   #minmaxscaler is applied to mm_columns from schema.yaml-->Annual premium
                ],
                remainder = "passthrough"
            )

            #wrapping everything in a single pipeline
            final_pipeline = Pipeline(steps = [("Preprocessor", preprocessor)])
            logging.info("Final pipeline ready!")
            logging.info("Exited get_transformer_object method of DataTransformation class")
            return final_pipeline

        except Exeption as e:
            logging.exception("Exception occurred in get_transformer_object method of DataTransformation class")
            raise MyException(e, sys) from e


    def _map_gender_column(self, df):
        """
        Map gender column to 0 for Female and 1 for Male"""
        logging.info("Mapping 'Gender' column to binary values")
        df['Gender'] = df['Gender'].map({"Female": 0, "Male": 1}).astype(int)
        return df 

    
    def _create_dummy_columns(self, df):
        """Create dummy variables for categorical features"""
        logging.info("Creating dummy variables for categorical features")
        df = pd.get_dummies(df, drop_first = True)
        return df 

#this function was specifically written to apply the above dummy column function
    def _rename_columns(self, df):
        """Rename specific columns and ensure integer types for dummy columns"""
        logging.info("Renaming specific columns and casting to int")
        df = df.rename(columns = {
            "Vehicle_Age < 1 Year": "Vehicle_Age_lt_1_Year",
            "Vehicle_Age_> 2 Years": "Vehicle_Age_gt_2_Years"
        })
        for col in ["Vehicle_Age_lt_1_Year", "Vehicle_Age_gt_2_Years", "Vehicle_Damage_Yes"]:
            if col in df.columns:
                df[col] = df[col].astype('int')
        return df 


    def _drop_id_column(self, df):
        """Drop the 'id' column if it exists"""
        logging.info("Dropping the 'id' column")
        drop_col = self._schema_config['drop_columns']
        if drop_col in df.columns:
            df = df.drop(drop_col, axis = 1)
        return df 


    
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        """
        Initiates data transformation component from the pipeline.
        """
        try:
            logging.info("Data transformation started!!")
            if not self.data_validation_artifact.validation_status:  #agar validation status true nahi raha toh exception raise hoga
                raise Exception(self.data_validation_artifact.message)  #aur message raise hojayega

            
            #reads and load train and test data
            train_df = self.read_data(file_path = self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(file_path = self.data_ingestion_artifact.test_file_path)
            logging.info("Train-test data loaded")

            #split features and target in both train and test data
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis = 1)
            target_feature_train_df = train_df[TARGET_COLUMN]

            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis = 1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            logging.info("Input and Target cols defined for both train and test df.")


            #apply custom transactions in specified sequence 
            input_feature_train_df = self._map_gender_column(input_feature_train_df)
            input_feature_train_df = self._drop_id_column(input_feature_train_df)
            input_feature_train_df = self._create_dummy_columns(input_feature_train_df)
            input_feature_train_df = self._rename_columns(input_feature_train_df)

            input_feature_test_df = self._map_gender_column(input_feature_test_df)
            input_feature_test_df = self._drop_id_column(input_feature_test_df)
            input_feature_test_df = self._create_dummy_columns(input_feature_test_df)
            input_feature_test_df = self._rename_columns(input_feature_test_df)
            logging.info("Custom transformations applied to train and test data")

            logging.info("Starting data transformation")
            preprocessor = self.get_data_transformer_object()   #ye uppar vale function ko call kr raha hai jo end meh pura pipeline return krdega
            logging.info("Get the preprocessor object")

            logging.info("Initializing transformation for training data")
            input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df)
            logging.info("Initializing transformation for testing data")
            input_feature_test_arr = preprocessor.transform(input_feature_test_df)
            logging.info("Transformation done end to end to train-test df")

            logging.info("Applying SMOTEENN for handling imbalanced dataset")
            smt = SMOTEENN(sampling_strategy="minority")
            input_feature_train_final, target_feature_train_final = smt.fit_resample(
                input_feature_train_arr, target_feature_train_df
            )
            input_feature_test_final, target_feature_test_final = smt.fit_resample(
                input_feature_test_arr, target_feature_test_df
            )
            logging.info("SMOTEENN applied to train-test df")

            #combines features+target into one array-->model expects .npy file
            train_arr = np.c_[input_feature_train_final, np.array(target_feature_train_final)]
            test_arr = np.c_[input_feature_test_final, np.array(target_feature_test_final)]
            logging.info("feature-target concatenation done for train-test df.")
            #np.c_ is the shorthand of np.concatenate()

            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor) #saving our preprocessor object
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array = test_arr)
            logging.info("Saving transformation object and transformed files")

            logging.info("Data transformation completed successfully!")

            return DataTransformationArtifact(
                transformed_object_file_path = self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path = self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path = self.data_transformation_config.transformed_test_file_path 
            )

        except Exception as e:
            raise MyException(e, sys) from e



