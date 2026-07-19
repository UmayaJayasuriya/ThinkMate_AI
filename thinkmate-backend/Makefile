.PHONY: install run docker-up docker-down docker-logs test test-unit clean pull-model

install:
	pip install -r requirements.txt

run:
	uvicorn app:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f backend

pull-model:
	docker exec -it thinkmate_ollama ollama pull llama3.1

test:
	pytest tests/ -v

test-unit:
	pytest tests/ -v -m "not integration"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
