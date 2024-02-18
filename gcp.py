import logging
from api import configure_routing
from flask import Flask

from storage.firestore import FirestoreUpdater


gunicorn_logger = logging.getLogger('gunicorn.error')
app = Flask(__name__)
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

configure_routing(app, FirestoreUpdater())
