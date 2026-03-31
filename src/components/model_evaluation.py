from src.entity.config_entity import ModelEvaluationConfig 
from src.entity.artifact_entity import ModelTrainerArtifact, DataIngestionArtifact, ModelEvaluationArtifact 
from sklearn.metrics import f1_score 
from src.exception import MyException 
from src.constants import TARGET_COLUMN
from src.logger import logging 
from src.utils.main_utils import load_object 
import sys 
import pandas as pd 
from typing import Optional 
from src.entity.s3_estimator import Proj1Estimator 
from dataclasses import dataclass 


@dataclass 
class EvaluateModelResponse:  #pipeline k next stage ko ye object pass hota hai
    trained_model_f1_score: float   #trained model ka score
    best_model_f1_score: float    #production model ka score 
    is_model_accepted: bool 
    difference: float   #trained model aur production model k score ka difference



#ye class basically trained model ko production model(s3 me jo h) se compare krta hai and decides if trained should be deployed or not
class ModelEvaluation:

    def __init__(self, model_eval_config: ModelEvaluationConfig, data_ingestion_artifact: DataIngestionArtifact, 
                 model_trainer_artifact: ModelTrainerArtifact):
        try:
            self.model_eval_config = model_eval_config 
            self.data_ingestion_artifact = data_ingestion_artifact 
            self.model_trainer_artifact = model_trainer_artifact 
        except Exception as e:
            raise MyException(e, sys) from e
        

    def get_best_model(self) -> Optional[Proj1Estimator]:
        """
        Method Name :   get_best_model
        Description :   This function is used to get model from production stage.
        
        Output      :   Returns model object if available in s3 storage
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            bucket_name = self.model_eval_config.bucket_name
            model_path = self.model_eval_config.s3_model_key_path   #this basically loads production model
            proj1_estimator = Proj1Estimator(bucket_name = bucket_name,
                                             model_path = model_path)
            
            if proj1_estimator.is_model_present(model_path = model_path):
                return proj1_estimator   #agar s3 meh production model exist krta hai toh vo return krdo else none
            return None
        except Exception as e:
            raise MyException(e, sys) 
        
#niche saare helper functions hai taaki test data ko bhi trained data ke format meh convert kr sake jisse model prediction kr paaye
    def _map_gender_column(self, df):
        """Map gender column to 0 for female and 1 for male"""
        logging.info("Mapping 'Gender' column to binary values")
        df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1}).astype(int)
        return df 


    def _create_dummy_columns(self, df):
        """Create dummy variabels for categorical features"""
        logging.info("Create dummy variables for categorical features")
        categorical_columns = df.select_dtypes(include=["object", "category"]).columns
        if len(categorical_columns) == 0:
            return df
        df = pd.get_dummies(df, columns=categorical_columns, drop_first=True)
        return df 


    def _rename_columns(self, df):
        """Rename specific columns and ensure integer types for dummy columns"""
        logging.info("Renaming specific columns and casting to int")
        df = df.rename(columns = {
            "Vehicle_Age_< 1 Year": "Vehicle_Age_lt_1_Year",
            "Vehicle_Age_> 2 Years": "Vehicle_Age_gt_2_Years" 
        })   
        for col in ["Vehicle_Age_lt_1_Year", "Vehicle_Age_gt_2_Years", "Vehicle_Damage_Yes"]:
            if col in df.columns:
                df[col] = df[col].astype('int')
        return df 
    

    def _drop_id_columns(self, df):
        """Drop the 'id' column if it exists"""
        logging.info("Dropping the 'id' column")
        id_columns = [col for col in ["_id", "id"] if col in df.columns]
        if id_columns:
            df = df.drop(id_columns, axis=1)
        return df
    

    def evaluate_model(self) -> EvaluateModelResponse:
        """
        Method Name :   evaluate_model
        Description :   This function is used to evaluate trained model 
                        with production model and choose best model 
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            #test data load
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            x, y = test_df.drop(TARGET_COLUMN, axis = 1), test_df[TARGET_COLUMN]  #splits x and y

            logging.info("Test data loaded and now transforming it for prediction...")

            #performing preprocessing funcs on test data since we will eval it later
            x = self._drop_id_columns(x)
            x = self._map_gender_column(x)
            x = self._create_dummy_columns(x)
            x = self._rename_columns(x)

            trained_model = load_object(file_path = self.model_trainer_artifact.trained_model_file_path)  #model.pkl ko return krega
            logging.info("Trained model loaded/exists")
            trained_model_f1_score = self.model_trainer_artifact.metric_artifact.f1_score  #uss local trained model ka f1 score 
            logging.info(f"F1 score of this model: {trained_model_f1_score}")

            best_model_f1_score = None 
            best_model = self.get_best_model() 
            if best_model is not None:
                logging.info(f"Computing f1 score for production model...")
                y_hat_best_model = best_model.predict(x)
                best_model_f1_score = f1_score(y, y_hat_best_model)  #production model ka evaluation
                logging.info(f"F1_score-Production Model: {best_model_f1_score}, F1_score-Trained Model: {trained_model_f1_score}")

            tmp_best_model_score = 0 if best_model_f1_score is None else best_model_f1_score   #agar s3 meh koi bhi model rahega nahi(yaani no score) toh iska value 0 hojayega
            result = EvaluateModelResponse(trained_model_f1_score = trained_model_f1_score,
                                             best_model_f1_score = best_model_f1_score,
                                             is_model_accepted = trained_model_f1_score > tmp_best_model_score,  #if trained model score > production model--> accept or reject
                                             difference = trained_model_f1_score - tmp_best_model_score)
            logging.info(f"Result: {result}")
            return result 
        
        except Exception as e:
            raise MyException(e, sys)
        
#initiate_model_evaluation() evaluation run karta hai
#aur ek structured artifact return karta hai
#jisme accept/reject decision + paths + score difference hota hai.
    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        """
        Method Name :   initiate_model_evaluation
        Description :   This function is used to initiate all steps of the model evaluation
        
        Output      :   Returns model evaluation artifact
        On Failure  :   Write an exception log and then raise an exception
        """  
        try:
            print("--------------------------------------------------------------------------------")
            logging.info("Initialized Model Evaluation")
            evaluate_model_response = self.evaluate_model()  #calls the above eval function
            s3_model_path = self.model_eval_config.s3_model_key_path  #fetching s3 model path-->model.pkl

            model_evaluation_artifact = ModelEvaluationArtifact(
                is_model_accepted = evaluate_model_response.is_model_accepted,
                s3_model_path = s3_model_path,
                trained_model_path = self.model_trainer_artifact.trained_model_file_path,
                changed_accuracy = evaluate_model_response.difference
            )

            logging.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            return model_evaluation_artifact 
        except Exception as e:
            raise MyException(e, sys) from e
            

    


