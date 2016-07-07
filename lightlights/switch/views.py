# -*- coding: utf-8 -*-
from flask import Blueprint, url_for, request, jsonify,  render_template
from lightlights.switch.model import Switch
from lightlights.utils import jsonifyReturn
from lightlights.extentions import csrf, db
from sqlalchemy.exc import IntegrityError
from lightlights.lights.model import Light

switch = Blueprint('switch', __name__)


@switch.route('/')
def switch_list():
    switchs = Switch.get_switches()
    return render_template('switch/switch_list.html', switchs=switchs)


@switch.route('/<switch_id>/edit')
@csrf.exempt
def edit(switch_id):
    switch = Switch.get(switch_id)
    lights = Light.get_lights()
    bind_lights = switch.lights
    for bind in bind_lights:
        for light in lights:
            if light.id == bind.id:
                if not hasattr(light, 'checked'):
                    light.checked = True
            else:
                if not hasattr(light, 'checked'):
                    light.checked = False

    if switch:
        return render_template('switch/edit_switch.html', switch=switch, lights=lights)


@switch.route('/<switch_id>/update', methods=['post'])
@csrf.exempt
def update(switch_id):
    lights = request.form.getlist('lights')
    name = request.form.get('name')
    eui = request.form.get('eui')
    group_eui = request.form.get('groupEUI')

    return 'hello'


@switch.route('/switch/add', methods=['POST'])
@csrf.exempt
def switch_add():
    switch = Switch()
    if not request.form.get('eui'):
        return jsonifyReturn(success=False, status_code=422, code=4000, message='EUI不能为空')
    if not request.form.get('name'):
        return jsonifyReturn(success=False, status_code=422, code=4000, message='名称不能为空')
    if not request.form.get('group_eui'):
        return jsonifyReturn(success=False, status_code=422, code=4000, message='GroupEUI不能为空')

    switch.eui = request.form.get('eui').strip().upper()
    switch.name = request.form.get('name').strip()
    switch.group_eui = request.form.get('group_eui').strip().upper()
    try:
        db.session.add(switch)
        db.session.commit()
        return jsonifyReturn(message=u'添加{}成功'.format(switch.name), data={'switch': {'id': switch.id, 'name': switch.name,
                                              'eui': switch.eui, 'group_eui': switch.group_eui}})
    except IntegrityError as e:
        return jsonifyReturn(success=False, message=e.orig.message, status_code=422)


@switch.route('/switch/update', methods=['POST'])
@csrf.exempt
def switch_update():
    if request.form.get('switch_id'):
        switch = Switch.get(request.form.get('switch_id'))
        if switch:
            if not request.form.get('eui'):
                return jsonifyReturn(success=False, status_code=422, code=4000, message='EUI不能为空')
            if not request.form.get('name'):
                return jsonifyReturn(success=False, status_code=422, code=4000, message='名称不能为空')
            if not request.form.get('group_eui'):
                return jsonifyReturn(success=False, status_code=422, code=4000, message='GroupEUI不能为空')

            switch.eui = request.form.get('eui').strip().upper()
            switch.name = request.form.get('name').strip()
            switch.group_eui = request.form.get('group_eui').strip().upper()
            try:
                db.session.add(switch)
                db.session.commit()
                return jsonifyReturn(message=u'更新 {} 成功'.format(switch.name), data={'switch': {'id': switch.id, 'name': switch.name,
                                                      'eui': switch.eui, 'group_eui': switch.group_eui}})
            except IntegrityError as e:
                return jsonifyReturn(success=False, message=e.orig.message, status_code=422)
        else:
            return jsonifyReturn(success=False, message='开关不存在', status_code=422)


@switch.route('/switch/delete', methods=['POST'])
@csrf.exempt
def switch_delete():
    if request.form.get('switch_id'):
        switch = Switch.get(request.form.get('switch_id'))
        if not switch:
            return jsonifyReturn(success=False, message='不存在该灯管', status_code=422)
        try:
            db.session.delete(switch)
            db.session.commit()
            return jsonifyReturn(message='删除成功')
        except Exception as e:
            return jsonifyReturn(success=False, message='删除异常', status_code=422)
    else:
        return jsonifyReturn(success=False, message='参数不对', status_code=422)