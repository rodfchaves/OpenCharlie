from settings import *
from debug import *
import psycopg2

CONN = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)

cursor = CONN.cursor()


def store_conversation_log(transcription, tool, role):
    try:
        insert_query = """
        INSERT INTO conversation_log (transcription, tool, role) VALUES (%s, %s, %s);
        """
        data_to_insert = (transcription, tool, role)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        cursor.close()
        CONN.close()
    except Exception as e:
        error_handler(e)

def store_error_log(message):
    try: 
        insert_query = """
        INSERT INTO error_log (message) VALUES (%s);
        """
        data_to_insert = (message)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        cursor.close()
        CONN.close()
    except Exception as e:
        error_handler(e)

def store_alarm(alarm_trigger, timezone, status):
    try:
        insert_query = """
        INSERT INTO alarms (alarm_trigger, timezone, status) VALUES (%s, %s, %s);
        """
        data_to_insert = (alarm_trigger, timezone, status)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        cursor.close()
        CONN.close()
    except Exception as e:
        error_handler(e)

def get_alarms():
    try:
        cursor.execute("SELECT * FROM alarms;")
        results = cursor.fetchall()
        cursor.close()
        CONN.close()
        return results

    except Exception as e:
        error_handler(e)

def store_settings(constant_name, value):
    try:
        insert_query = """
        UPDATE settings SET constant_name = %s, value = %s);
        """
        data_to_insert = (constant_name, value)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        cursor.close()
        CONN.close()
    except Exception as e:
        error_handler(e)


def get_values(table):
    try:
        insert_query = """
        SELECT * FROM %s;
        """
        cursor.execute("SELECT * FROM %s")
        data_to_insert = (table)
        cursor.execute(insert_query, data_to_insert)
        settings = cursor.fetchall()
        results = {}
        for (a,b) in settings:
            results[a] = b
        return results
    except Exception as e:
        error_handler(e)

