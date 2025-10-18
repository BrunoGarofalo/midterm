
import os
import pandas as pd
from decimal import Decimal
from app.logger import logger
from app.config import (
    CALCULATOR_MAX_HISTORY_SIZE, 
    CALCULATOR_AUTO_SAVE, 
    CALCULATOR_DEFAULT_ENCODING,
    CALCULATOR_HISTORY_DIR,
    CSV_HISTORY_FILE,
    TXT_HISTORY_FILE
)


class LoggingObserver:
    def __init__(self, log_file=TXT_HISTORY_FILE):

        # Ensure the history directory exists
        os.makedirs(CALCULATOR_HISTORY_DIR, exist_ok=True)

        self.log_file = os.path.join(CALCULATOR_HISTORY_DIR, log_file)
        # self.history = []

    # #method that adds the new calculation log to 
    # def update(self, final_message):

    #     #update the last operation but do not save
    #     if len(self.history) > CALCULATOR_MAX_HISTORY_SIZE:
    #         self.history = self.history[-CALCULATOR_MAX_HISTORY_SIZE:]

    #     logger.info(f"LoggingObserver updated with operation: {final_message}")

    #method that adds the new calculation log to 
    def save_history(self, history):
        if len(history) >0:
            with open(self.log_file, "w",encoding=CALCULATOR_DEFAULT_ENCODING) as file:
                        for entry in history:
                            file.write(entry + "\n")
            logger.info(f"Full history saved to {self.log_file}")
            print("✅ Full history successfully saved to history_log.txt")
        else:
            logger.warning("Attempted to save empty history, No history to be saved")
            print(f"❌ No history to be saved")


    def detach(self, final_message):
        self.history.remove(final_message)
        logger.info(f"LoggingObserver detached operation: {final_message}")




   

class AutosaveObserver:

    def __init__(self, log_file=CSV_HISTORY_FILE):
        # Ensure the history directory exists
        os.makedirs(CALCULATOR_HISTORY_DIR, exist_ok=True)

        self.log_file = os.path.join(CALCULATOR_HISTORY_DIR, log_file)
        self.columns = ["timestamp", "operation", "operand1", "operand2", "result"]

        # If the file doesn't exist or is empty, create a new one
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
            self.df = pd.DataFrame(columns=self.columns)
            self.df.to_csv(self.log_file, index=False)
            logger.info(f"AutosaveObserver initialized new file: {self.log_file}")
        else:
            self.df = pd.read_csv(self.log_file)
            logger.info(f"AutosaveObserver loaded existing file: {self.log_file}")
    

    #method that adds the new calculation log to 
    def update(self, final_message):

        #get individual values from message
        message_values = final_message.split("|")

        #zip values to create key-value pairs and create dict
        values_dict = dict(zip(self.columns, message_values))

        #create new data row in pandas
        new_row = pd.DataFrame([values_dict])

        #add new row to df
        self.df = pd.concat([self.df, new_row], ignore_index=True)

        # Trim to max history size
        if len(self.df) > CALCULATOR_MAX_HISTORY_SIZE:
            self.df = self.df.tail(CALCULATOR_MAX_HISTORY_SIZE)

        # Only save automatically if enabled
        if CALCULATOR_AUTO_SAVE:
            self.df.to_csv(self.log_file, index=False, encoding=CALCULATOR_DEFAULT_ENCODING)
            logger.info(f"AutosaveObserver auto-saved operation: {final_message}")

        logger.info(f"AutosaveObserver updated with operation: {final_message}")

    
    def delete_history(self):
        self.df = pd.DataFrame(columns=self.columns)  
        self.df.to_csv(self.log_file, index=False)   

        logger.warning(f"AutosaveObserver cleared history in {self.log_file}")

    
    def load_history(self):
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
            logger.warning("AutosaveObserver attempted to load history but file is missing/empty")
            print("❌ No saved history to load")
            return []
        
        df = pd.read_csv(self.log_file, encoding=CALCULATOR_DEFAULT_ENCODING)
        if df.empty:
            logger.warning("AutosaveObserver attempted to load history but file is empty")
            print("❌ History file is empty")
            return []

        loaded_calculations = []

        for _, row in df.iterrows():
            operation_record = f"{row["timestamp"]}|{row["operation"]}|{row["operand1"]}|{row["operand2"]}|{row["result"]}"
            loaded_calculations.append(operation_record)

        logger.info(f"AutosaveObserver loaded {len(loaded_calculations)} history entries from {self.log_file}")
        return loaded_calculations


class Subject:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, final_message):
        for observer in self.observers:
            observer.update(final_message)
