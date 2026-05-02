.PHONY: install-dev lint format type test check run

install-dev:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt -r requirements-dev.txt

lint:
	python -m ruff check .

format:
	python -m ruff format .

type:
	python -m mypy app.py src

test:
	python -m pytest -q

check:
	python -m ruff format --check .
	python -m ruff check .
	python -m mypy app.py src
	python -m pytest -q

run:
	python app.py
