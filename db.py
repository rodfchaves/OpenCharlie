from debug import *
from db_settings import *
from psycopg2.sql import SQL, Identifier

def store_conversation_log(transcription, tool, role):
    """
    Store the conversation log in the database
    transcription: the transcription of the conversation
    tool: the tool used to transcribe the conversation
    role: the role of the user in the conversation
    
    """

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
        print_me('Conversation log saved successfully!')
    except Exception as e:
        CONN.rollback()
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()

def store_alarm(alarm_trigger, timezone, status):
    try:
        insert_query = """
        INSERT INTO alarms (alarm_trigger, timezone, status) VALUES (%s, %s, %s);
        """
        data_to_insert = (alarm_trigger, timezone, status)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        print_me('Alarm data saved successfully!')
    except Exception as e:
        CONN.rollback()
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()

def get_alarms():
    try:
        cursor.execute("SELECT * FROM alarms;")
        results = cursor.fetchall()
        return results
    except Exception as e:
        CONN.rollback()
        error_handler(e)
    finally:
        cursor.close()
        CONN.close()


def store_data(table, name, value):
    try:
        insert_query = """
        INSERT INTO %s (name, value) VALUES (%s, %s) ON CONFLICT DO UPDATE SET value = %s;
        """
        data_to_insert = (table, name, value, name, value)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        print_me('Form data saved successfully!')
    except Exception as e:
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
    try:
        insert_query = """
        INSERT INTO tokens (name, value) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET value = %s;
        """
        data_to_insert = (name, json_data, json_data)
        cursor.execute(insert_query, data_to_insert)
        CONN.commit()
        print_me('Token data saved successfully!')
    except Exception as e:
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
    try:
        insert_query = "SELECT * FROM {};"
        cursor.execute(SQL(insert_query).format(Identifier(table)), (table))
        settings = cursor.fetchall()
        results = {}
        for (a,b,c) in settings:
            results[a] = b
        return results    
    except Exception as e:
        error_handler(e)   

def get_token(name):
    """
    Get the token from the database
    name: the name of the token

    Returns:
    The value of the token

    """ 
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
    except Exception as e:
        error_handler(e)


