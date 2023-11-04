import os

from dotenv import load_dotenv

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXP_MINUTES = os.getenv("TOKEN_EXP_MINUTES")

load_dotenv()
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
ENVIRONMENT = os.getenv('ENVIRONMENT')

SHOW_DOCS_ENVIRONMENT = ('dev',)

# Mail variables
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_FROM = os.getenv('MAIL_FROM')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_STARTTLS = os.getenv('MAIL_STARTTLS')
MAIL_SSL_TLS = os.getenv('MAIL_SSL_TLS')
USE_CREDENTIALS = os.getenv('USE_CREDENTIALS')
VALIDATE_CERTS = os.getenv('VALIDATE_CERTS')
SUPPRESS_SEND = os.getenv('SUPPRESS_SEND')
