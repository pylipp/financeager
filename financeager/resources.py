from flask_restful import Resource, reqparse

import os.path

from . import CONFIG_DIR
from .server import Server


os.makedirs(CONFIG_DIR, exist_ok=True)  # pragma: no cover

SERVER = Server(data_dir=CONFIG_DIR)

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
print_parser.add_argument("filters", type=dict)

update_parser = reqparse.RequestParser()
update_parser.add_argument("name")
update_parser.add_argument("value", type=float)
update_parser.add_argument("category")
update_parser.add_argument("date")
update_parser.add_argument("frequency")
update_parser.add_argument("start")
update_parser.add_argument("end")


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
