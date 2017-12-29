#pylint: disable=R0201
from flask_restful import Resource, reqparse

from .server import Server


SERVER = Server()

copy_parser = reqparse.RequestParser()
copy_parser.add_argument("destination_period_name", required=True)
copy_parser.add_argument("source_period_name", required=True)
copy_parser.add_argument("eid", required=True, type=int)
copy_parser.add_argument("table_name")

put_parser = reqparse.RequestParser()
put_parser.add_argument("name", required=True)
put_parser.add_argument("value", required=True, type=float)
put_parser.add_argument("category", default=None)
put_parser.add_argument("date", default=None)
put_parser.add_argument("frequency", default=None)
put_parser.add_argument("start", default=None)
put_parser.add_argument("end", default=None)
put_parser.add_argument("table_name", default=None)

print_parser = reqparse.RequestParser()
print_parser.add_argument("name", default=None)
print_parser.add_argument("category", default=None)
print_parser.add_argument("date", default=None)

update_parser = reqparse.RequestParser()
update_parser.add_argument("name", default=None)
update_parser.add_argument("value", default=None, type=float)
update_parser.add_argument("category", default=None)
update_parser.add_argument("date", default=None)
update_parser.add_argument("frequency", default=None)
update_parser.add_argument("start", default=None)
update_parser.add_argument("end", default=None)


class PeriodsResource(Resource):
    def post(self):
        return SERVER.run("list")


class PeriodResource(Resource):
    def get(self, period_name):
        args = print_parser.parse_args()
        return SERVER.run("print", period=period_name, **args)

    def post(self, period_name):
        args = put_parser.parse_args()
        return SERVER.run("add", period=period_name, **args)


class EntryResource(Resource):
    def get(self, period_name, table_name, eid):
        response = SERVER.run("get", period=period_name, table_name=table_name,
                eid=eid)

        if "error" in response:
            response = (response, 404)

        return response

    def delete(self, period_name, table_name, eid):
        response = SERVER.run("rm", period=period_name, table_name=table_name,
                eid=eid)

        if "error" in response:
            response = (response, 404)

        return response

    def patch(self, period_name, table_name, eid):
        args = update_parser.parse_args()
        response = SERVER.run("update", period=period_name,
                table_name=table_name, eid=eid, **args)

        if "error" in response:
            response = (response, 400)

        return response


class CopyResource(Resource):
    def post(self):
        args = copy_parser.parse_args()
        response = SERVER.run("copy", **args)

        if "error" in response:
            response = (response, 404)

        return response


class ShutdownResource(Resource):
    def post(self):
        SERVER.run("stop")
        from flask import request
        f = request.environ.get("werkzeug.server.shutdown")
        if f is None:
            return {"error": "Not running with the Werkzeug Server"}, 500
        f()
