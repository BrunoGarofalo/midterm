
import os
import pandas as pd
from decimal import Decimal
from app.logger import logger
from app.config import (
    CALCULATOR_AUTO_SAVE, 
    CALCULATOR_DEFAULT_ENCODING,
    CALCULATOR_HISTORY_DIR,
    CSV_HISTORY_FILE,
    TXT_HISTORY_FILE,
    CSV_COLUMNS
)
import json

from app.exceptions import FileAccessError



# ------------------------------------------------------------
# LoggingObserver
# ------------------------------------------------------------
class LoggingObserver:
    def __init__(self, log_file=TXT_HISTORY_FILE):
        try:

            # Ensure the history directory exists
            os.makedirs(CALCULATOR_HISTORY_DIR, exist_ok=True)
            self.log_file = os.path.join(CALCULATOR_HISTORY_DIR, log_file)
            logger.info(f"✅ LoggingObserver initialized with log file: {self.log_file}")

        
        except Exception as e:
            logger.error(f"❌ Failed to initialize LoggingObserver  {e}")
            raise FileAccessError(f"❌ Failed to create log directory: {e}")

    # method that appends new calculation to TXT file
    def update(self,  message):
        if not message:
            logger.warning("❌ Logging Observer attempted to save new calculation. Caclulation data unavailable.")
            return
        

        try:
            with open(self.log_file, "a",encoding=CALCULATOR_DEFAULT_ENCODING) as file:
                file.write(json.dumps(message) + "\n")
                logger.info(f"✅ Logging Observer saved new calculation to {self.log_file}")
        
        except Exception as e:
            logger.error(f"❌ LoggingObserver failed to save: {e}")



# ------------------------------------------------------------
# AutosaveObserver
# ------------------------------------------------------------
class AutosaveObserver:

    def __init__(self, log_file=CSV_HISTORY_FILE):
        try:

            # Ensure the history directory exists
            os.makedirs(CALCULATOR_HISTORY_DIR, exist_ok=True)

            self.log_file = os.path.join(CALCULATOR_HISTORY_DIR, log_file)
            
            # If the file doesn't exist or is empty, create a new one
            if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
                self.df = pd.DataFrame(columns=CSV_COLUMNS)
                self.df.to_csv(self.log_file, index=False)
                logger.info(f"✅ AutosaveObserver initialized new file: {self.log_file}")
            else:
                self.df = pd.read_csv(self.log_file)
                logger.info(f"✅ AutosaveObserver loaded existing file: {self.log_file}")
        
        except Exception as e:
            logger.error("❌ Failed to initialize AutosaveObserver.")
            raise FileAccessError(f"❌ Error initializing AutosaveObserver: {e}")
        
    def set_columns(self, columns):
        self.columns = columns


    #method that adds the new calculation log to 
    def update(self, message):

        try:

            if not message:
                logger.warning("❌ No data to save in AutosaveObserver.")
                return
            

            #create new data row in pandas
            new_row = pd.DataFrame([message])

            #add new row to df
            self.df = pd.concat([self.df, new_row], ignore_index=True)

            # Only save automatically if enabled
            if CALCULATOR_AUTO_SAVE:
                try:

                    self.df.to_csv(self.log_file, index=False, encoding=CALCULATOR_DEFAULT_ENCODING)

                    logger.info(f"✅ AutosaveObserver auto-saved operation: {message}")

                except Exception as e:
                    logger.error(f"❌ AutosaveObserver failed to save: {e}")

            
        except Exception as e:
            logger.error(f"❌ Error updating AutosaveObserver: {e}")
            raise FileAccessError(f"❌ Error in AutosaveObserver: {e}")

    

# ------------------------------------------------------------
# Subject
# ------------------------------------------------------------
class Subject:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        #attach observers to Subject
        self.observers.append(observer)

    def final_message_split(self, message):
            #get individual values from message by splitting on |
            message_values = message.split(",")

            #if there are fewer values then the required number of columns
            if len(message_values) != len(CSV_COLUMNS):
                logger.error(f"❌ Mismatch in expected columns for Observers: {message}")
                return

            #zip values to create key-value pairs and create dict
            values_dict = dict(zip(CSV_COLUMNS, message_values))

            return values_dict


    def notify(self, message):

        final_message = self.final_message_split(message)
    
        for observer in self.observers:
            observer.update(final_message)

