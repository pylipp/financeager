VERSION=$(shell python -c "import financeager; print(financeager.__version__)")

.PHONY: all test install upload tag publish coverage lint format style-check

all:
	@echo "Available targets: install, test, upload, tag, publish, coverage, lint, format, style-check"

install:
	pip install -U -e .

test:
	python setup.py test

upload: README.md setup.py
	rm -f dist/*
	python setup.py bdist_wheel --universal
	twine upload dist/*

tag:
	git tag v$(VERSION)
	git push --tags
	hub release create -m "Release v$(VERSION)" v$(VERSION)

publish: tag upload

coverage:
	coverage run --source financeager setup.py test
	coverage report
	coverage html

lint:
	pre-commit run --all-files flake8

format:
	pre-commit run --all-files yapf
	pre-commit run --all-files end-of-file-fixer
	pre-commit run --all-files trailing-whitespace

style-check: format lint
