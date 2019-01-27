"""Utilities to create flask webservice."""

from flask import Flask
from flask_restful import Api

from . import PERIODS_TAIL, COPY_TAIL, init_logger, setup_log_file_handler
from .resources import (PeriodsResource, PeriodResource, EntryResource,
                        CopyResource)


def create_app(config=None):
    """Create web app with RESTful API built from resources. The function is
    named such that the flask cli detects it as app factory method."""
    app = Flask(__name__)
    app.config.update(config or {})
    api = Api(app)

    api.add_resource(PeriodsResource, PERIODS_TAIL)
    api.add_resource(CopyResource, COPY_TAIL)
    api.add_resource(PeriodResource, "{}/<period_name>".format(PERIODS_TAIL))
    api.add_resource(EntryResource,
                     "{}/<period_name>/<table_name>/<eid>".format(PERIODS_TAIL))

    setup_log_file_handler()
    # Propagate flask log messages to financeager logs
    init_logger("flask.app")

    return app
