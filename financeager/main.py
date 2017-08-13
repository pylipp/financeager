from __future__ import unicode_literals
from financeager import cli

def main():
    args = parse_command()
    cli.main(vars(args))
