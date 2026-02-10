import logging 
import os 
from logging.handlers import RotatingFileHandler
from from_root import from_root
from datetime import datetime

#constants for log config
LOG_DIR = 'logs'
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"  #log files ka naam-->02_09_2026_14_30_45.log
MAX_LOG_SIZE = 5 * 1024 * 1024  #5mb
BACKUP_COUNT = 3  #Number of backup log files to keep   (ye rotating file handler ka parameter h)


#setting up log file path
log_dir_path = os.path.join(from_root(), LOG_DIR)  #root path aur /logs ko join krke path banayega-->
os.makedirs(log_dir_path, exist_ok = True)   #Basically root directory meh 'logs' naam ka folder create krdega
log_file_path = os.path.join(log_dir_path, LOG_FILE)   #ab uss logs vale folder k andhar jo files store honge, ye uska address hai



def configure_logger():
    """
    Configures logging with a rotator file handler and a console handler
    """
    #create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    #define formatter
    formatter = logging.Formatter("[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s")

    #file handler with rotation
    file_handler = RotatingFileHandler(log_file_path, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)  #Rotating matlab: log file size limit cross kare toh automatically new file create ho
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    #console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    #add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


#calling our function to configure the logger
configure_logger()
