from flask_restful import Resource, reqparse

from financeager.server import Server
from financeager.period import Period


SERVER = Server()

put_parser = reqparse.RequestParser()
put_parser.add_argument("name", required=True)
put_parser.add_argument("value", required=True)
put_parser.add_argument("category", default=None)
put_parser.add_argument("date", default=None)
put_parser.add_argument("repetitive", default=False, type=list)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument("name", required=True)
delete_parser.add_argument("category", default=None)
delete_parser.add_argument("date", default=None)


class PeriodsResource(Resource):
    def get(self):
        return SERVER.periods()

class PeriodResource(Resource):
    def get(self, period_name):
        return SERVER.run("print", period=period_name)

    def post(self, period_name):
        args = put_parser.parse_args()
        return SERVER.run("add", period=period_name, **args)

    def delete(self, period_name):
        args = delete_parser.parse_args()
        return SERVER.run("rm", period=period_name, **args)
