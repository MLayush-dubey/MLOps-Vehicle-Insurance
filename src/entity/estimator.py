import sys

import pandas as pd
from pandas import DataFrame
from sklearn.pipeline import Pipeline

from src.exception import MyException
from src.logger import logging


class TargetValueMapping:
    def __init__(self):
        self.yes: int = 0
        self.no: int = 1
    def _asdict(self):
        return self.__dict__
    def reverse_mapping(self):
        mapping_response = self._asdict()
        return dict(zip(mapping_response.values(), mapping_response.keys()))


class MyModel:
    def __init__(self, preprocessing_object: Pipeline, trained_model_object: object):
        """
        :param preprocessing_object: Input Object of preprocesser
        :param trained_model_object: Input Object of trained model 
        """
        self.preprocessing_object = preprocessing_object
        self.trained_model_object = trained_model_object

    def predict(self, dataframe: pd.DataFrame) -> DataFrame:
        """
        Function accepts preprocessed inputs (with all custom transformations already applied),
        applies scaling using preprocessing_object, and performs prediction on transformed features.
        """
        try:
            logging.info("Starting prediction process")

            #step 1: Apply scaling transformations using the pre-trained preprocessing object
            transformed_feature = self.preprocessing_object.transform(dataframe)  #since inference hai toh sirf .transform() use kr rahe hai

            #step 2: Perform prediction with the trained model
            logging.info("Using the trained model to get prediction")
            predictions = self.trained_model_object.predict(transformed_feature)
            return predictions

        except Exception as e:
            raise MyException(e, sys) from e

        
#since ye class ka output MyModel hai, toh if in case we are training multiple models then it gives us the name of the specified model

    def __repr__(self):  #developer facing representation
        return f"{type(self.trained_model_object).__name__}()"


    def __str__(self):  #user facing representation
        return f"{type(self.trained_model_object).__name__}()"

#without the above __repr__ and __str__ it prints something like--> <MyModel object at 0x7f8b2c1d>
#with the above, it prints something like--> RandomForestClassifier()




