from flask import Flask
from application import detector

UPLOAD_FOLDER = 'application/upload_files'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from application import views
