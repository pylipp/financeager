"""Webservice resources as end points of financeager REST API."""
import json

import flask
from flask_restful import Resource, reqparse

from . import init_logger

logger = init_logger(__name__)

copy_parser = reqparse.RequestParser()
copy_parser.add_argument("destination_period", required=True)
copy_parser.add_argument("source_period", required=True)
copy_parser.add_argument("eid", required=True, type=int)
copy_parser.add_argument("table_name")

put_parser = reqparse.RequestParser()
put_parser.add_argument("name", required=True)
put_parser.add_argument("value", required=True, type=float)
put_parser.add_argument("category")
put_parser.add_argument("date")
put_parser.add_argument("frequency")
put_parser.add_argument("start")
put_parser.add_argument("end")
put_parser.add_argument("table_name")

print_parser = reqparse.RequestParser()
print_parser.add_argument("filters")

update_parser = reqparse.RequestParser()
update_parser.add_argument("name")
update_parser.add_argument("value", type=float)
update_parser.add_argument("category")
update_parser.add_argument("date")
update_parser.add_argument("frequency")
update_parser.add_argument("start")
update_parser.add_argument("end")


class LogResource(Resource):
    """Custom class to facilitate request logging and safe execution of server
    commands."""

    def __init__(self, server, *args, **kwargs):
        """Store reference to application Server object."""
        super().__init__(*args, **kwargs)
        self.server = server

    def run_safely(self, command, error_code=500, **kwargs):
        """Wrapper function for running commands on server. Returns server
        response, if erroneous, including an appropriate error code.
        If an unexpected exception is caught, the method logs it and returns an
        internal server error.
        """
        try:
            response = self.server.run(command, **kwargs)

            if "error" in response:
                response = (response, error_code)
        except Exception:
            logger.exception("Unexpected error")
            response = ({"error": "unexpected error"}, 500)

        return response

    def dispatch_request(self, *args, **kwargs):
        """Log content of request that is about to be dispatched."""
        logger.debug(
            "Dispatching {r} holding {{data: {r.data}, "
            "values: {r.values}, json: {r.json}}}".format(r=flask.request))
        return super().dispatch_request(*args, **kwargs)


class PeriodsResource(LogResource):
    def post(self):
        return self.run_safely("list")


class PeriodResource(LogResource):
    def get(self, period_name):
        args = json.loads(flask.request.json or "{}")
        return self.run_safely(
            "print", error_code=400, period=period_name, **args)

    def post(self, period_name):
        args = put_parser.parse_args()
        return self.run_safely(
            "add", error_code=400, period=period_name, **args)


class EntryResource(LogResource):
    def get(self, period_name, table_name, eid):
        return self.run_safely(
            "get",
            error_code=404,
            period=period_name,
            table_name=table_name,
            eid=eid)

    def delete(self, period_name, table_name, eid):
        return self.run_safely(
            "rm",
            error_code=404,
            period=period_name,
            table_name=table_name,
            eid=eid)

    def patch(self, period_name, table_name, eid):
        args = update_parser.parse_args()
        return self.run_safely(
            "update",
            error_code=400,
            period=period_name,
            table_name=table_name,
            eid=eid,
            **args)


class CopyResource(LogResource):
    def post(self):
        args = copy_parser.parse_args()
        return self.run_safely("copy", error_code=404, **args)
