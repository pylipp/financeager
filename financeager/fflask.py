"""Utilities to create flask webservice."""
import os

from flask import Flask
from flask_restful import Api

from . import PERIODS_TAIL, COPY_TAIL, init_logger, setup_log_file_handler
from .server import Server
from .resources import (PeriodsResource, PeriodResource, EntryResource,
                        CopyResource)


def create_app(data_dir=None, config=None):
    """Create web app with RESTful API built from resources. The function is
    named such that the flask cli detects it as app factory method.
    If 'data_dir' is given, a directory is created to store application data,
    and the log file handler is set up.
    An instance of 'server.Server' is created, passing 'data_dir'. If 'data_dir'
    is not given, the application data is stored in memory and will be lost when
    the app terminates.
    'config' is a dict of configuration variables that flask understands.
    """
    if data_dir is not None:
        os.makedirs(data_dir, exist_ok=True)
        setup_log_file_handler()

    app = Flask(__name__)
    app.config.update(config or {})
    api = Api(app)

    server = Server(data_dir=data_dir)

    api.add_resource(
        PeriodsResource, PERIODS_TAIL, resource_class_args=(server,))
    api.add_resource(CopyResource, COPY_TAIL, resource_class_args=(server,))
    api.add_resource(
        PeriodResource,
        "{}/<period_name>".format(PERIODS_TAIL),
        resource_class_args=(server,))
    api.add_resource(
        EntryResource,
        "{}/<period_name>/<table_name>/<eid>".format(PERIODS_TAIL),
        resource_class_args=(server,))

    # Propagate flask log messages to financeager logs
    init_logger("flask.app")

    return app
