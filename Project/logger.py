from datetime import datetime
import os


folder_name = "log_download_output"
file_name = "log.txt"

def get_current_date_time():
    # Get the current date and time
    now = datetime.now()
    
    # Format the date and time separately
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    return current_date, current_time

def logging(url, text, exec_time):
  log_path = os.path.join(folder_name, file_name)
  with open(log_path, "a", encoding="utf-8") as file:
     current_date, current_time = get_current_date_time()
     if exec_time == 0:
       log_entry     = f"Timestamp {current_time}, {current_date} , execution method: {text},  {url}\n"
     else:
       log_entry = f"Timestamp {current_time}, {current_date} , execution method: {text}, time taken: {exec_time} seconds\n"
     file.write(log_entry)
     