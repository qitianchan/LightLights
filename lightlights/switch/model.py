# -*- coding: utf-8 -*-
from lightlights.extentions import db


class Switch(db.Model):
    __tablename__ = 'switchs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    eui = db.Column(db.String(64), nullable=False, unique=True)                     # 设备EUI,用于接收消息
    group_eui = db.Column(db.String(64), nullable=False, unique=True)               # 组播EUI,用于发送开关命令


    @classmethod
    def get_switches(cls):
        return cls.query.all()

    @classmethod
    def get(cls, switch_id):
        return cls.query.filter(cls.id == switch_id).first()