sources = {{ cookiecutter.pkg_name }}

.PHONY: test format lint unittest coverage pre-commit clean
test: format lint unittest

format:
	@echo "Run isort"
	poetry run isort $(sources) tests
	@echo "_____"
	@echo "Run black"
	poetry run black $(sources) tests
	@echo "_____"

lint:
	@echo "Run pylint"
	poetry run pylint $(sources) tests
	@echo "_____"
	@echo "Run pydocstyle"
	poetry run pydocstyle $(sources) tests
	@echo "_____"
	@echo "Run mypy"
	poetry run mypy $(sources) tests
	@echo "_____"

unittest:
	poetry run pytest

coverage:
	poetry run pytest --cov=$(sources) --cov-branch --cov-report=term-missing tests

pre-commit:
	poetry run pre-commit run --all-files

clean:
	rm -rf **/.mypy_cache **/.pytest_cache
	rm -rf *.egg-info
	rm -rf .tox dist site
	rm -rf coverage.xml .coverage
