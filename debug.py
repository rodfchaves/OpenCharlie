import traceback
import platform
from settings import DEBUG
from db import store_error_log

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

    """
    To handle errors and exceptions

    Parameters:
    e (error): Exception

    Returns:
    str: A message with the error details.

    Notes:
    If DEBUG is set as True inside the settings.py file, it prints the messages.
    """

    tb = traceback.extract_tb(e.__traceback__)
    os_info = get_os_info()
    last_tb = tb[-1]
    file_name = last_tb.filename  
    line_no = last_tb.lineno  
    func_name = last_tb.name
    message = f"Exception: {e}, File: {file_name}, Line: {line_no}, Function: {func_name}, OS Info: {os_info}"
    store_error_log(message)

    if DEBUG == True:
        print(message)

    return message

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
    
