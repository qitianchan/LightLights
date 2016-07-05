# -*- coding: utf-8 -*-
import eventlet
eventlet.monkey_patch()
from flask import Blueprint, redirect, request, jsonify, render_template
from lightlights.lights.model import Light
from lightlights.extentions import csrf, db
from sqlalchemy.exc import IntegrityError
from lightlights.utils import jsonifyReturn
light = Blueprint('light', __name__)


@light.route('/')
@light.route('/lights')
def light_list():
    lights = Light.get_lights()
    return render_template('lights/light_list.html', lights=lights)


@light.route('/light/add', methods=['POST'])
@csrf.exempt
def light_add():
    light = Light()
    if not request.form.get('eui'):
        return jsonifyReturn(success=False, status_code=422, code=4000, message='EUI不能为空')
    light.eui = request.form.get('eui').strip().upper()
    if not request.form.get('identifier'):
        return jsonifyReturn(success=False, status_code=422, code=4000, message='编号不能为空')
    light.identifier = request.form.get('identifier').strip().upper()
    try:
        db.session.add(light)
        db.session.commit()
        return jsonifyReturn(data={'light': {'id': light.id, 'identifier': light.identifier,
                                             'eui': light.eui, 'on_count': light.on_count, 'status': light._get_status()}})
    except IntegrityError as e:
        return jsonifyReturn(success=False, message='EUI已经存在', status_code=422)


@light.route('/light/update', methods=['POST'])
@csrf.exempt
def light_update():
    if request.form.get('light_id'):
        light = Light.get(request.form.get('light_id'))
        if light:
            if not request.form.get('eui'):
                return jsonifyReturn(success=False, status_code=422, code=4000, message='EUI不能为空')
            light.eui = request.form.get('eui').strip().upper()
            if not request.form.get('identifier'):
                return jsonifyReturn(success=False, status_code=422, code=4000, message='编号不能为空')
            light.identifier = request.form.get('identifier').strip().upper()
            try:
                db.session.add(light)
                db.session.commit()
                return jsonifyReturn(data={'light': {'id': light.id, 'identifier': light.identifier,
                                                     'eui': light.eui, 'on_count': light.on_count,
                                                     'status': light._get_status()}})
            except IntegrityError as e:
                return jsonifyReturn(success=False, message='EUI已经存在', status_code=422)
        else:
            return jsonifyReturn(success=False, message='不存在该灯管', status_code=422)
    else:
        return jsonifyReturn(success=False, message='参数不对', status_code=422)


@light.route('/light/delete', methods=['POST'])
@csrf.exempt
def light_delete():
    if request.form.get('light_id'):
        light = Light.get(request.form.get('light_id'))
        if not light:
            return jsonifyReturn(success=False, message='不存在该灯管', status_code=422)
        try:
            db.session.delete(light)
            db.session.commit()
            return jsonifyReturn(message='删除成功')
        except Exception as e:
            return jsonifyReturn(success=False, message='删除异常', status_code=422)
    else:
        return jsonifyReturn(success=False, message='参数不对', status_code=422)


@light.route('/light/reset', methods=['POST'])
@csrf.exempt
def light_reset():
    if request.form.get('light_id'):
        light = Light.get(request.form.get('light_id'))
        if not light:
            return jsonifyReturn(success=False, message='不存在该灯管', status_code=422)
        try:
            # todo: 发送关灯命令
            light.on_count = 0
            db.session.add(light)
            db.session.commit()
            return jsonifyReturn(message='重置成功', data={'light': {'id': light.id, 'identifier': light.identifier,
                                                     'eui': light.eui, 'on_count': light.on_count,
                                                     'status': light._get_status()}})
        except Exception as e:
            return jsonifyReturn(success=False, message='重置异常', status_code=422)
    else:
        return jsonifyReturn(success=False, message='参数不对', status_code=422)