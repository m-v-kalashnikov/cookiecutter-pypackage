sources = hooks

.PHONY: test format lint unittest coverage pre-commit clean
test: format lint tox

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
	poetry run pytest --ignore={{cookiecutter.project_slug}}

tox:
	@echo "Run yox"
	poetry run tox
	@echo "_____"

clean:
	rm -rf .mypy_cache **/.mypy_cache
	rm -rf .pytest_cache **/.pytest_cache
	rm -rf *.egg-info
	rm -rf .tox dist site
	rm -rf coverage.xml .coverage
