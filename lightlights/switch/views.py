# -*- coding: utf-8 -*-
from flask import Blueprint, url_for, request, jsonify
from lightlights.switch.model import Switch

switch = Blueprint('switch', __name__)


@switch.route('/')
def switch_list():
    return 'switch list'

