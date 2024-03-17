import os
import time
import mysql.connector
from MySQLBrain import MySQLBrain

import mysql.connector
from mysql.connector import Error

host = os.getenv("DATABASE_HOST")
user = os.getenv("DATABASE_USERNAME")
passwd = os.getenv("DATABASE_PASSWORD")
db = os.getenv("DATABASE_NAME")


try:
    print("Connecting to the database...")
    db_manager = MySQLBrain(host, user, passwd, db_name=db)
    db_manager.list_databases()  # List all databases
    print("Connected:", db_manager)
except Error as e:
    print("Error while connecting to MySQL", e)
