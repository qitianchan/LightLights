# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CsrfProtect
from flask_socketio import SocketIO

db = SQLAlchemy()

csrf = CsrfProtect()

socketio = SocketIO()