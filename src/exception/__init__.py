import sys
import logging 

def error_message_detail(error: Exception, error_detail: sys) -> str:
    """
    Extracts details error information including filename, line number, and the error message

    :param error: The exception that occurred
    :param error_detail: The sys module to access traceback details
    :return: A formatted error message string
    """
    #extracts traceback details(exception information)
    _, _, exc_tb = error_detail.exc_info()   #since sys module ko hum error detail bula rahe hai, this method is of sys module--> returns 3 objects(exception_type, exception_value, traceback_object)
    #so basically we are ignoring the first two objects which is exception type and value, we are only extracting traceback_object-->file name, line number and error details milega


    #get the file name where the exception occuurred
    file_name = exc_tb.tb_frame.f_code.co_filename  #basically uss traceback se humlog file name extract kar rahe h


    #create a formatted error message string with file name, line number and the actual error
    line_number = exc_tb.tb_lineno   #since exc_tb-->exception traceback. Iss method k andhar tb_lineno gives you the line number, vahi simply nikaal rahe h

    error_message = f"Error occurred in python script: [{file_name}] at line number [{line_number}]: {str(error)}"

    #log the error for better tracking
    logging.error(error_message)  #will look like--> [ 2026-02-09 14:30:45 ] root - ERROR - Error occurred in python script: [data_ingestion.py at line number 45]: division by zero

    return error_message 


#custom class bana rahe h jo ki inherit kr raha h from Exception class
class MyException(Exception):
    """
    Custom exception class for handling errors in the US visa application
    """
    def __init__(self, error_message: str, error_detail: sys):
        """
        Initializes the USVisaException with a detailed error message

        :param error_message: A string describes the error
        :param error_detail: The sys module to access the traceback details.
        """

        #call the base class constructor with the error message--> Exception class(parent class) ka __init__ access karke humlog humhare constructor ko call kr rahe h
        super().__init__(error_message)

        #format the error message using the detailed error_message detail function
        self.error_message = error_message_detail(error_message, error_detail)  #calling our function from above and storing the error message and error detail 


def __str__(self) -> str:
    """
    Returns the string representation of the error message.
    """
    return self.error_message  #simply return krdega error message ko


