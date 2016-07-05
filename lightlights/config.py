# -*- coding: utf-8 -*-
import os


class DefaultConfig(object):

    _basedir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

    DEBUG = True
    TESTING = False

    # Logs
    # If SEND_LOGS is set to True, the admins (see the mail configuration) will
    # recieve the error logs per email.
    SEND_LOGS = False

    # The filename for the info and error logs. The logfiles are stored at
    # flaskbb/logs
    INFO_LOG = "info.log"
    ERROR_LOG = "error.log"

    # Default Database
    DATABASE_PATH = os.path.join(_basedir, 'lights.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH


    # This will print all SQL statements
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # Security
    # This is the secret key that is used for session signing.
    # You can generate a secure key with os.urandom(24)
    SECRET_KEY = '\x99A\x8f\x0f\xe5tG\xe6f\t\xfe\xe1Y\xe9X,\xb6\xdf,\xea\x12q\xc9\xc5'

    # Protection against form post fraud
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = "reallyhardtoguess"

    # Searching
    WHOOSH_BASE = os.path.join(_basedir, "whoosh_index")

    # Auth
    LOGIN_VIEW = "auth.login"
    REAUTH_VIEW = "auth.reauth"
    LOGIN_MESSAGE_CATEGORY = "error"

    # Caching
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 60

    ## Captcha
    RECAPTCHA_ENABLED = False
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = "your_public_recaptcha_key"
    RECAPTCHA_PRIVATE_KEY = "your_private_recaptcha_key"
    RECAPTCHA_OPTIONS = {"theme": "white"}

    ## Mail
    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USE_TLS = False
    MAIL_USERNAME = "noreply@example.org"
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = ("Default Sender", "noreply@example.org")
    # Where to logger should send the emails to
    ADMINS = ["admin@example.org"]

    # Flask-Redis
    REDIS_ENABLED = False
    REDIS_URL = "redis://:123456@183.230.40.230:6379"
    REDIS_DATABASE = 0

    # URL Prefixes
    USER_URL_PREFIX = "/user"
    AUTH_URL_PREFIX = "/auth"
    LIGHT_URL_PREFIX = "/light"
    SWITCH_URL_PREFIX = "/switch"

    # Smart Button
    GATEWAY_ID = 'a2d790e1-1670-1217-0000-000db93db700'
    ORGANIZATION = 'niot'
    LINKLAB_USERNAME = 'niot.user'
    LINKLAB_PASSWORD = 'Ni0t!0715'

    # Pagination
    PER_PAGE = 15


    # Ourself Server websocket infomation
    LORA_APP_EUI = 'BE7A0000000001C0'
    LORA_TOKEN = 'WxwwWkBUdm5jLpDDZbkExw'
    LORA_HOST = '183.230.40.231'
    LORA_PORT = 8100
    NAMESPACE_PATH = '/test'

