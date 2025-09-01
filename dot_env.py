import os
from dotenv import load_dotenv
load_dotenv('.env')

DISEASE_TRAIN_DATA='app/csvFile/DISEASE_TRAIN.csv'
DISEASE_TEST_DATA='app/csvFile/DISEASE_TEST.csv'

DB_STORAGE_USER = 'app/csvFile/users.csv'
DB_STORAGE_PREDICTION = 'app/csvFile/predictions.csv'
DB_STORAGE_QUERY = 'app/csvFile/query.csv'

MY_EMAIL_FOR_CONTACT = os.getenv('ver')
EMAIL_PASSWORD = os.getenv('email_password')
ADMIN_PASSWORD = os.getenv('admin_pass')

HTML_APP_TITLE  = os.getenv('appname')
APP_VERSION = os.getenv('ver')
UPDATED_ON = os.getenv('date')
SUPPORT_EMAIL= os.getenv('s_email')
SUPPORT_PHONE= os.getenv('s_phone')