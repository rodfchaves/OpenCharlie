import psycopg2

#DATABASE
DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_NAME = "gmcharlie"

CONN = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)

cursor = CONN.cursor()