"""Utilities to create and launch flask webservice."""

from flask import Flask
from flask_restful import Api

from .resources import (PeriodsResource, PeriodResource, EntryResource,
                        CopyResource)

# URL endpoints
PERIODS_TAIL = "/financeager/periods"
COPY_TAIL = PERIODS_TAIL + "/copy"


def create_app(config=None):
    """Create web app with RESTful API built from resources."""
    app = Flask(__name__)
    app.config.update(config or {})
    api = Api(app)

    api.add_resource(PeriodsResource, PERIODS_TAIL)
    api.add_resource(CopyResource, COPY_TAIL)
    api.add_resource(PeriodResource,
            "{}/<period_name>".format(PERIODS_TAIL))
    api.add_resource(EntryResource,
        "{}/<period_name>/<table_name>/<eid>".format(PERIODS_TAIL))

    return app


def launch_server(debug=False, host=None):
    """Create and launch flask webservice application. Debug mode and host name
    are optional.
    """
    app = create_app(config={"DEBUG": debug, "SERVER_NAME": host})
    app.run()
