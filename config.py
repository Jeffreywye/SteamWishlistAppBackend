"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

# Flask configs
DEBUG = False
SECRET_KEY = environ.get('SECRET_KEY')

# SQL Alchemy configs
user = environ.get('PG_USER')
password = environ.get('PG_PASS')
host = environ.get('PG_HOST')
dbName = environ.get('DBNAME')
# dbPath = path.join(basedir, "Models" , dbName)

# Local mysql connection
# conn = "mysql://{0}:{1}@{2}/{3}".format(user, password, host, dbName)

# Local Postgres Connection
# conn = "postgresql://{0}:{1}@{2}/{3}".format(user, password, host, dbName)

# Production Connection
conn = environ.get('DATABASE_URL')

# print(conn)
SQLALCHEMY_DATABASE_URI = conn
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# jwt-extended-configs
JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = 900
JWT_REFRESH_TOKEN_EXPIRES = 7200

# Flask-Mail configs
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = environ.get('EMAIL')
MAIL_PASSWORD = environ.get('EMAIL_PASS')
MAIL_USE_TLS = False
MAIL_USE_SSL = True