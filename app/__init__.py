from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from flask_mail import Mail
mail = Mail(app) 

from app import routes