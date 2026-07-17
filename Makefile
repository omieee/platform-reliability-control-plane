.PHONY: test lint format fix ready

test:
	python -m pytest

lint:
	python -m ruff check .

format:
	python -m ruff format .

fix:
	python -m ruff check . --fix
	python -m ruff format .

ready: fix test lint