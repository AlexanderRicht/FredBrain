from MySQLBrain import MySQLBrain
import os

host = os.getenv("DATABASE_HOST")
user = os.getenv("DATABASE_USERNAME")
passwd = os.getenv("DATABASE_PASSWORD")
db = os.getenv("DATABASE_NAME")

db_manager = MySQLBrain(host, user, passwd, db_name=db)
