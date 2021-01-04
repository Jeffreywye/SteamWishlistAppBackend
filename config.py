"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

# Flask configs
DEBUG = True
SECRET_KEY = environ.get('SECRET_KEY')

# SQL Alchemy configs
user = environ.get('USER')
password = environ.get('PASSWORD')
host = environ.get('HOST')
dbName = environ.get('DBNAME')
# dbPath = path.join(basedir, "Models" , dbName)
conn = "mysql://{0}:{1}@{2}/{3}".format(user, password, host, dbName)
# print(conn)
SQLALCHEMY_DATABASE_URI = conn
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# jwt-extended-configs
JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = 900
JWT_REFRESH_TOKEN_EXPIRES = 7200