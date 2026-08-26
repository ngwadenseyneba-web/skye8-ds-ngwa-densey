import os


DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "port": 5432,
    "dbname": "Skye8",
    "password": os.getenv("DB_PASSWORD"),
}