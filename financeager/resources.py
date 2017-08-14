from flask_restful import Resource, reqparse

from .server import Server


SERVER = Server()

put_parser = reqparse.RequestParser()
put_parser.add_argument("name", required=True)
put_parser.add_argument("value", required=True, type=float)
put_parser.add_argument("category", default=None)
put_parser.add_argument("date", default=None)
put_parser.add_argument("repetitive", default=False, type=list)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument("name", required=True)
delete_parser.add_argument("category", default=None)
delete_parser.add_argument("date", default=None)

periods_parser = reqparse.RequestParser()
periods_parser.add_argument("running", default=False)

print_parser = reqparse.RequestParser()
print_parser.add_argument("name", default=None)
print_parser.add_argument("category", default=None)
print_parser.add_argument("date", default=None)


class PeriodsResource(Resource):
    def post(self):
        args = periods_parser.parse_args()
        return SERVER.run("list", **args)

class PeriodResource(Resource):
    def get(self, period_name):
        args = print_parser.parse_args()
        return SERVER.run("print", period=period_name, **args)

    def post(self, period_name):
        args = put_parser.parse_args()
        return SERVER.run("add", period=period_name, **args)

    def delete(self, period_name):
        args = delete_parser.parse_args()
        response = SERVER.run("rm", period=period_name, **args)

        if "error" in response:
            response = (response, 404)

        return response

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

class ShutdownResource(Resource):
    def post(self):
        SERVER.run("stop")
        from flask import request
        f = request.environ.get("werkzeug.server.shutdown")
        if f is None:
            return {"error": "Not running with the Werkzeug Server"}, 500
        f()
