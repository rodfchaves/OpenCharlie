"""
This module contains the functions to interact with the database
"""

from debug import *
from db_settings import *
from psycopg2.sql import SQL, Identifier
import psycopg2

def db_connect():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST
        )
        return conn
    except psycopg2.Error as e:
        error_handler(e)

CONN = db_connect()

cursor = CONN.cursor()


def store_conversation_log(transcription, tool, role):
    """
    Store the conversation log in the database
    transcription: the transcription of the conversation
    tool: the tool used to transcribe the conversation
    role: the role of the user in the conversation
    
    """
    CONN = db_connect()
    cursor = CONN.cursor()
    try:
        print(f'transcription: {transcription}')
        print(f'tool: {tool}')
        print(f'role: {role}')
        insert_query = """
        INSERT INTO conversation_log (transcription, tool, role) VALUES (%s, %s, %s);
        """
        data_to_insert = (transcription, tool, role)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        print('Conversation log saved successfully!')
    except psycopg2.Error as e:
        CONN.rollback()
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()

def store_alarm(alarm_trigger, timezone, status):
    CONN = db_connect()
    cursor = CONN.cursor()
    try:
        insert_query = """
        INSERT INTO alarms (alarm_trigger, timezone, status) VALUES (%s, %s, %s);
        """
        data_to_insert = (alarm_trigger, timezone, status)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        print('Alarm data saved successfully!')
    except psycopg2.Error as e:
        CONN.rollback()
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()

def get_alarms():
    CONN = db_connect()
    cursor = CONN.cursor()
    try:
        cursor.execute("SELECT * FROM alarms;")
        results = cursor.fetchall()
        return results
    except psycopg2.Error as e:
        CONN.rollback()
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()


def store_data_admin(items):
    CONN = db_connect()
    cursor = CONN.cursor()
    try:
        print(f'items: {items}')

        for item in items:
            insert_query = """
            INSERT INTO admin (name, value) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET name = %s, value = %s;
            """
            data_to_insert = (item[0], item[1], item[0], item[1])
            print(f"Data to insert: {data_to_insert}")
            cursor.execute(insert_query, data_to_insert)
            CONN.commit()
            print('Form data saved successfully!')
    except psycopg2.Error as e:
        CONN.rollback()
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()

def store_data_settings(items):
    CONN = db_connect()
    cursor = CONN.cursor()
    try:
        print(f'items: {items}')
        for item in items:
            insert_query = """
            INSERT INTO settings (name, value) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET name = %s, value = %s;
            """
            data_to_insert = (item[0], item[1], item[0], item[1])
            print(f"Data to insert: {data_to_insert}")
            cursor.execute(insert_query, data_to_insert)
            CONN.commit()
            print('Form data saved successfully!')
    except psycopg2.Error as e:
        CONN.rollback()
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()

def store_token(name, json_data):
    """
    Store the token in the database
    name: the name of the token
    json_data: the value of the token (already passed through json.dumps())
    """
    print("Storing token: " + name + " with value: " + json_data)
    CONN = db_connect()
    cursor = CONN.cursor()
    try:
        insert_query = """
        INSERT INTO tokens (name, value) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET value = %s;
        """
        data_to_insert = (name, json_data, json_data)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        print('Token data saved successfully!')
    except psycopg2.ProgrammingError as e:
        error_handler(e)   
        conn.rollback()
    except psycopg2.InterfaceError as e:
        error_handler(e)   
        conn = db_connect()
        cursor = conn.cursor() 
    except psycopg2.Error as e:
        CONN.rollback()
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()

def get_values(table):
    """
    Get the values from the database
    table: the table to get the values from

    Returns:
    A dictionary of the values from the table

    """
    CONN = db_connect()
    cursor = CONN.cursor()
    try:
        insert_query = "SELECT * FROM {};"
        cursor.execute(SQL(insert_query).format(Identifier(table)), (table))
        settings = cursor.fetchall()
        results = {}
        for (a,b,c) in settings:
            results[a] = b
        return results 
    except psycopg2.ProgrammingError as e:
        error_handler(e)   
        conn.rollback()
    except psycopg2.InterfaceError as e:
        error_handler(e)   
        conn = db_connect()
        cursor = conn.cursor()   
    except psycopg2.Error as e:
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()   

def get_token(name):
    """
    Get the token from the database
    name: the name of the token

    Returns:
    The value of the token

    """ 
    CONN = db_connect()
    cursor = CONN.cursor()
    try:
        insert_query = """
        SELECT * FROM tokens WHERE name = %s;
        """
        data_to_insert = (name,)
        cursor.execute(insert_query, data_to_insert)
        settings = cursor.fetchall()
        results = {}
        for (a,b, c) in settings:
            results[a] = b
        return results
    except psycopg2.Error as e:
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()


