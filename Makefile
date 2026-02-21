.PHONY: dev seed list events events-rf tournaments-gt

dev:
	uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000

seed:
	uv run python run.py seed

list:
	uv run python run.py list

events:
	uv run python run.py events

events-rf:
	uv run python run.py events-rf

tournaments-gt:
	uv run python run.py tournaments-gt
