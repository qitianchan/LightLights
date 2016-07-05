# -*- coding: utf-8 -*
from flask import jsonify


def jsonifyReturn(success=True, status_code=201, code=1000, message='Success', data=None):
    res = jsonify({'success': success, 'code': code, 'message': message, 'data': data})
    res.status_code = status_code
    return res
