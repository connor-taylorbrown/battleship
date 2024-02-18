from threading import Thread
from api import configure_routing
from flask import Flask

from storage.tinydb import TinyDbUpdater, UpdateListener


def create_app():
    ''' Default factory method for Flask CLI runner '''
    app = Flask(__name__)
    listener = UpdateListener(app.logger)
    thread = Thread(target=listener.run, daemon=True)
    thread.start()

    return configure_routing(app, TinyDbUpdater(listener, 'json/games.json'))
