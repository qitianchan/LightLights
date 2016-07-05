# -*- coding: utf-8 -*-
import logging
async_mode = None

async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

from flask import Flask
from threading import Thread
from lightlights.lights.views import light
from lightlights.switch.views import switch
from lightlights.extentions import db, csrf, socketio
from lightlights.lora.receive import ws_listening


def create_app(config=None):
    """Creates the app."""

    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Use the default config and override it afterwards
    app.config.from_object('lightlights.config.DefaultConfig')
    # Update the config
    app.config.from_object(config)

    configure_extensions(app)
    configure_blueprint(app)
    init_app(app)
    app.debug = app.config['DEBUG']
    with app.app_context():
        db.create_all()
    return app


def configure_blueprint(app):
    app.register_blueprint(light)
    app.register_blueprint(switch, url_prefix=app.config['SWITCH_URL_PREFIX'])


def configure_extensions(app):

    db.init_app(app)
    # Flask-WTF CSRF
    csrf.init_app(app)
    socketio.init_app(app, async_mode=async_mode)


thread = None
def init_app(app):
    logging.info('init_app')
    @app.before_first_request
    def before_first_request():
        try:
            global thread
            if thread is None:
                ws_listening()
        except Exception as e:
            raise e

if __name__ == '__main__':
    app = create_app()
    app.debug = True
    # socketio.run(app, host='183.230.40.230', port=8077)
    socketio.run(app, host='127.0.0.1', port=8077)
