format:
	ruff format .
	ruff check . --fix

lint:
	ruff check .

type-check:
	mypy .

app-run:
	python -m src.presentation.api.main

messaging-run:
	python -m src.presentation.messaging.main
