VERSION=$(shell python -c "import financeager; print(financeager.__version__)")

.PHONY: all test install tags upload tag publish coverage coverage-html lint

all:
	@echo "Available targets: install, test, upload, tag, publish, coverage, coverage-html, lint"

install:
	pip install -U -r requirements.txt -e .

test:
	@[ -z $$VIRTUAL_ENV ] && echo "Acticate financeager virtualenv." || python -m test.suites

tags:
	ctags -R .

README.rst: README.md
	pandoc README.md -o README.rst
	python setup.py check -rs

upload: README.rst setup.py
	rm -f dist/*
	python setup.py bdist_wheel --universal
	twine upload dist/*

tag:
	git tag v$(VERSION)
	git push --tags

publish: tag upload

coverage:
	@for f in test/test_*.py; do coverage run --source financeager --append $$f; done
	coverage report

coverage-html: coverage
	coverage html

lint:
	flake8 financeager test
