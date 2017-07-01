.PHONY: all test install tags

all:
	@echo "Available targets: install, test"

install:
	pip install -U -r requirements.txt -e .

test:
	@[ -z $$VIRTUAL_ENV ] && echo "Acticate financeager virtualenv." || python -m test.suites

tags:
	ctags -R .
