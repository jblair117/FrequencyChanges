from flask import Flask
from application import detector

UPLOAD_FOLDER = 'app/upload_files'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import views
