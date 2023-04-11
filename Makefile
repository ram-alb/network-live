install:
	poetry install

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=network_live --cov-report xml

lint:
	poetry run flake8 network_live

selfcheck:
	poetry check

check: selfcheck test lint

build: check
	poetry build

isort:
	poetry run isort network_live

.PHONY: install test lint selfcheck check build