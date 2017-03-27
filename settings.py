# coding: UTF-8
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SERVER_ADDRESS = os.environ.get('SERVER_ADDRESS')
SERVER_PORT = int(os.environ.get('SERVER_PORT'))
AWS_REGION = os.environ.get('AWS_REGION')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
ANDROID_ARN = os.environ.get('ANDROID_ARN')
IOS_ARN = os.environ.get('IOS_ARN')
TOPIC_ARN_LIST = os.environ.get('TOPIC_ARN_LIST').split(',')
