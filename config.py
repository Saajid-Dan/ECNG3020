import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # secure token
    SECRET_KEY = 'My Secret Key'
    
    # Sendgrid API key
    MAIL_PASSWORD = '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'
    MAIL_DEFAULT_SENDER = 'ecng3020.dashboard@gmail.com'            # Email sender and receiver

    # SQLite database location
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Project Directory
    # DIRECTORY = '/home/ECNG3020Dashboard/ECNG3020'      # Uncomment if on PythonAnywhere
    DIRECTORY = '.'                                      # Uncomment if not on PythonAnywhere