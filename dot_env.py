import os
from dotenv import load_dotenv
load_dotenv('.env')

DISEASE_TRAIN_DATA='app/csvFile/DISEASE_TRAIN.csv'
DISEASE_TEST_DATA='app/csvFile/DISEASE_TEST.csv'

DB_STORAGE_USER = 'app/csvFile/users.csv'
DB_STORAGE_PREDICTION = 'app/csvFile/predictions.csv'
DB_STORAGE_QUERY = 'app/csvFile/query.csv'

# MY_EMAIL_FOR_CONTACT = os.getenv('ver')
MY_EMAIL_FOR_CONTACT = os.environ.get('ver')
# EMAIL_PASSWORD = os.getenv('email_password')
EMAIL_PASSWORD = os.environ.get('email_password')
# ADMIN_PASSWORD = os.getenv('admin_pass')
ADMIN_PASSWORD = os.environ.get('admin_pass')

# HTML_APP_TITLE  = os.getenv('appname')
HTML_APP_TITLE  = os.environ.get('appname')
# APP_VERSION = os.getenv('ver')
APP_VERSION = os.environ.get('ver')
# UPDATED_ON = os.getenv('date')
UPDATED_ON = os.environ.get('date')
# SUPPORT_EMAIL= os.getenv('s_email')
SUPPORT_EMAIL= os.environ.get('s_email')
# SUPPORT_PHONE= os.getenv('s_phone')
SUPPORT_PHONE= os.environ.get('s_phone')
