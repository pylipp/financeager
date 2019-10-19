"""Utilities to create flask webservice."""
import os

from flask import Flask
from flask_restful import Api

from . import PERIODS_TAIL, COPY_TAIL, init_logger, setup_log_file_handler,\
    make_log_stream_handler_verbose
from .server import Server
from .resources import (PeriodsResource, PeriodResource, EntryResource,
                        CopyResource, VersionResource)

logger = init_logger(__name__)


def create_app(data_dir=None, config=None):
    """Create web app with RESTful API built from resources. The function is
    named such that the flask cli detects it as app factory method.
    The log file handler is set up very first.
    If 'data_dir' or the environment variable 'FINANCEAGER_DATA_DIR' is given, a
    directory is created to store application data.
    An instance of 'server.Server' is created, passing 'data_dir'. If 'data_dir'
    is not given, the application data is stored in memory and will be lost when
    the app terminates.
    'config' is a dict of configuration variables that flask understands.
    """
    setup_log_file_handler()

    # Propagate flask and werkzeug log messages to financeager logs
    init_logger("flask.app")
    init_logger("werkzeug")

    app = Flask(__name__)
    app.config.update(config or {})
    if app.debug:
        make_log_stream_handler_verbose()

    data_dir = data_dir or os.environ.get("FINANCEAGER_DATA_DIR")
    if data_dir is None:
        logger.warning("'data_dir' not given. Application data is stored in "
                       "memory and is lost when the flask app terminates. Set "
                       "the environment variable FINANCEAGER_DATA_DIR "
                       "accordingly for persistent data storage.")
    else:
        os.makedirs(data_dir, exist_ok=True)

    logger.debug("Created flask app {} - {} mode".format(
        app.name, "debug" if app.debug else "production"))

    server = Server(data_dir=data_dir)
    logger.debug(
        "Started financeager server with data dir '{}'".format(data_dir))

    api = Api(app)
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
    api.add_resource(
        VersionResource,
        '/version'
    )

    return app
