import os

from flask import Flask
from flask_cors import CORS

from .capture import bp_capture
from .training import bp_training
# from .recognition import bp_recognition


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(bp_capture)
    app.register_blueprint(bp_training)
    # app.register_blueprint(bp_recognition)

    return app
