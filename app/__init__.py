from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_compress import Compress

app = Flask(__name__)               # Instantiate Flask app
Compress(app)                       # Add text compression to HTML scripts
app.config.from_object(Config)      # Add configurations to Flask app from config.py
db = SQLAlchemy(app)                # Create SQLite database engine and add to Flask app
migrate = Migrate(app, db)          # Add migration support to the database

# Links URL routes and database models to the Flask app
from app import routes, models