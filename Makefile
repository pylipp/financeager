VERSION=$(shell python -c "import financeager; print(financeager.__version__)")

.PHONY: all test install tags upload tag publish coverage lint

all:
	@echo "Available targets: install, test, upload, tag, publish, coverage, lint"

install:
	pip install -U -e .

test:
	python setup.py test

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
	coverage run --source financeager setup.py test
	coverage report
	coverage html

lint:
	flake8 financeager test
