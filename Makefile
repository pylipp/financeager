VERSION=$(shell python -c "import pydartz; print(pydartz.__version__)")

.PHONY: all test install tags upload tag publish coverage coverage-html

all:
	@echo "Available targets: install, test, upload, tag, publish, coverage, coverage-html"

install:
	pip install -U -r requirements.txt -e .

test:
	@[ -z $$VIRTUAL_ENV ] && echo "Acticate financeager virtualenv." || python -m test.suites

tags:
	ctags -R .

README.rst: README.md
	pandoc README.md -o README.rst
	python setup.py check -r

upload: README.rst setup.py
	rm -f dist/*
	python setup.py bdist_wheel --universal
	twine upload dist/*

tag:
	# Make sure we're on the master branch
	ifneq "$(shell git rev-parse --abbrev-ref HEAD)" "master"
	$(error Not on master branch)
	endif

	git tag v$(VERSION)
	git push --tags

publish: tag upload

coverage:
	@for f in test/test_*.py; do coverage run --source financeager --append $$f; done
	coverage report

coverage-html: coverage
	coverage html
	xdg-open htmlcov/index.html
