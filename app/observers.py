
import os
import pandas as pd
from decimal import Decimal


class LoggingObserver:
    def __init__(self, log_file='history_log.txt'):
        # # Ensure the folder exists
        # folder = os.path.dirname(log_file)
        # os.makedirs(folder, exist_ok=True)
        self.log_file = log_file
        self.history = []

    #method that adds the new calculation log to 
    def update(self, final_message):

        #update the last operation but do not save
        self.history.append(final_message)

    #method that adds the new calculation log to 
    def save_history(self):
        if len(self.history) >0:
            with open("history_log.txt", "w") as file:
                        for entry in self.history:
                            file.write(entry + "\n")
            print("✅ Full history successfully saved to history_log.txt")
        else:
            print(f"❌ No history to be saved")

    def manual_history_save(self):
        #method that saves the new  

        #get individual values from message
        message_values = self.last_operation.split("|")

        #zip values to create key-value pairs and create dict
        values_dict = dict(zip(self.columns, message_values))

        #create new data row in pandas
        new_row = pd.DataFrame([values_dict])

        #add new row to df
        self.df = pd.concat([self.df, new_row], ignore_index=True)

        #save new df as a csv
        self.df.to_csv(self.log_file, index=False)

        print(f"✅ Log entry saved to {self.log_file}")


    def detach(self, final_message):
        self.history.remove(final_message)


    def show_history(self):
        if len(self.history) == 0:
            print("❌ No history to display!")
        else:
            print("\n👉 Full History:")
            for entry in self.history:
                print(entry)

    def delete_history(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
            print(f"✅ History succesfully deleted!")
        else:
            print("❌ No history to be displayed...yet!")
   

class AutosaveObserver:

    def __init__(self, log_file='history_log.csv'):
        self.log_file = log_file
        self.columns = ["timestamp", "operation", "operand1", "operand2", "result"]

        # If the file doesn't exist or is empty, create a new one
        if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
            self.df = pd.DataFrame(columns=self.columns)
            self.df.to_csv(log_file, index=False)
        else:
            self.df = pd.read_csv(log_file)
    

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

        #save new df as a csv
        self.df.to_csv(self.log_file, index=False)

        print(f"✅ Log entry saved to {self.log_file}")

    # def show_history(self):
    #     if not self.df.empty:
    #         print(self.df)
    #     else:
    #         print("❌ No history to be displayed...yet!")
    
    def delete_history(self):
        self.df = pd.DataFrame(columns=self.columns)  # clear in-memory DataFrame
        self.df.to_csv(self.log_file, index=False)    # overwrite CSV with empty DataFrame

    
    def load_history(self):
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
            print("❌ No saved history to load")
            return []
        
        df = pd.read_csv(self.log_file)
        if df.empty:
            print("❌ History file is empty")
            return []

        loaded_calculations = []

        for _, row in df.iterrows():
            operation_record = f"{row["timestamp"]}|{row["operation"]}|{row["operand1"]}|{row["operand2"]}|{row["result"]}"
            loaded_calculations.append(operation_record)

        return loaded_calculations


class Subject:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, final_message):
        for observer in self.observers:
            observer.update(final_message)
