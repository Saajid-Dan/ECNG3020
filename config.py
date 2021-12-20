import os

class Config(object):
    SECRET_KEY = 'My Secret Key'

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'SDan.Testing'
    MAIL_PASSWORD = 'P@55w0rd01'
    ADMINS = ['SDan.Testing@gmail.com']