# -*- coding: utf-8 -*-
from lightlights.extentions import db


class Switch(db.Model):
    __tablename__ = 'switchs'
    id = db.Column(db.Integer, primary_key=True)
    identifer = db.Column(db.String(64), nullable=True)
    eui = db.Column(db.String(64), nullable=False)
