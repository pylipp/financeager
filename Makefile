.PHONY: all test install release coverage lint format style-check

all:
	@echo "Available targets: install, test, release, coverage, lint, format, style-check"

install:
	python -m pip install -U -e .[develop]
	prek install --overwrite
	gitlint install-hook

test:
	python -m unittest

release:
	git push --tags origin master

coverage:
	coverage erase
	coverage run -m unittest
	coverage report
	coverage html

lint:
	prek run --all-files flake8

format:
	prek run --all-files black isort end-of-file-fixer trailing-whitespace

style-check: format lint
