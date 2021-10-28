from flask import Flask
from application import detector
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'application/upload_files'
# ALLOWED_EXTENSIONS = {'xes', 'pnml'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from application import views
