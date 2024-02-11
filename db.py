from settings import *
from debug import *
from db_settings import *
from psycopg2.sql import SQL, Identifier

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

def store_data(table, name, value):
    try:
        insert_query = """
        INSERT INTO %s (name, value) VALUES (%s, %s) ON CONFLICT DO UPDATE SET name = %s, value = %s WHERE constant_name = %s";
        """
        data_to_insert = (table, name, value, name, value, name)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        cursor.close()
        CONN.close()
        print_me('Form data saved successfully!')
    except Exception as e:
        error_handler(e)

def get_values(table):
    try:
        insert_query = "SELECT * FROM {}"
        data_to_insert = str(table)
        cursor.execute(SQL(insert_query).format(Identifier(data_to_insert)), (data_to_insert))
        settings = cursor.fetchall()
        results = {}
        for (a,b,c) in settings:
            results[a] = b
        return results
    except Exception as e:
        error_handler(e)


def get_token(name):
    try:
        insert_query = """
        SELECT * FROM tokens WHERE name = %s;
        """
        data_to_insert = (name)
        cursor.execute(insert_query, data_to_insert)
        settings = cursor.fetchall()
        results = {}
        for (a,b, c) in settings:
            results[a] = b
        return results
    except Exception as e:
        error_handler(e)


