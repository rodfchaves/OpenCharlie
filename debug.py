import traceback
import platform
from settings import *
from db_settings import *
from psycopg2.sql import SQL, Identifier

DEBUG = True
if DEBUG == True:
    print(f"DEBUG MODE: {DEBUG}")

def store_error_log(message):
    try: 
        print(f'message: {message}')
        insert_query = """
        INSERT INTO error_log (message) VALUES (%s);
        """
        data_to_insert = (str(message))
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        cursor.close()
        CONN.close()
    except Exception as e:
        print(e)

def get_os_info():
    info = {
        "OS": platform.system(),
        "OS Release": platform.release(),
        "OS Version": platform.version(),
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
    }
    return info

def error_handler(e):
    if DEBUG == True:

        """
        To handle errors and exceptions

        Parameters:
        e (error): Exception

        Returns:
        str: A message with the error details.

        Notes:
        If DEBUG is set as True inside the settings.py file, it prints the messages.
        """
        try:
            print(f'Error: {e}')
            tb = traceback.extract_tb(e.__traceback__)
            os_info = get_os_info()
            last_tb = tb[-1]
            file_name = last_tb.filename  
            line_no = last_tb.lineno  
            func_name = last_tb.name
            message = f"Exception: {e}, File: {file_name}, Line: {line_no}, Function: {func_name}, OS Info: {os_info}"
            store_error_log(message)

            print(message)

            return message
        except Exception as e: 
            print(e)

def print_me(text):
    """
    To print the text

    Parameters:
    text (str): The text to be printed.

    Returns:
    str: The text that was printed.

    Notes:
    If DEBUG is set as True inside the settings.py file, it prints the messages.
    """
    if DEBUG == True:
        print(text)
    
