# -*- coding: utf-8 -*-
from lightlights.extentions import db

light_switch_association_table = db.Table('ltsw_association',
                            db.Column('light_id', db.Integer, db.ForeignKey('lights.id')),
                            db.Column('switch_id', db.Integer, db.ForeignKey('switchs.id')))


class Light(db.Model):
    __tablename__ = 'lights'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(64), nullable=False)              # 编号
    eui = db.Column(db.String(64), nullable=False, unique=True)                     # lora设备eui
    on_count = db.Column(db.Integer, default=0)                         # 开动数
    # many-to-many
    switchs = db.relationship('Switch',
                              secondary=light_switch_association_table,
                              backref='lights')

    @classmethod
    def get_lights(cls):
        lights = []
        for light in cls.query.all():
            light.status = light._get_status()
            lights.append(light)
        return lights

    @classmethod
    def get(cls, light_id):
        return cls.query.filter(cls.id == light_id).first()

    def _get_status(self):
        return 'ON' if self.on_count else 'OFF'
