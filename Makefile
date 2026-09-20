instalar_dependencias:
	@echo "Instalando dependencias con uv (lee pyproject.toml y uv.lock)..."
	uv sync

run_test:
	@echo "Ejecutando test..."
	uv run pytest -v --cov=src --cov-report=html

run_linter_ruf:
	uv run ruff check --select E --select I

corregir_linter:
	uv run ruff check --fix --select E --select I . && uv run ruff format .
	uv run ruff check .

pre_commit:
	uvx pre-commit run --all-files

docker_test:
	docker build -f Dockerfile.test -t app-estadisticas-tests .
	docker run --rm app-estadisticas-tests

static_check:
	uv run mypy src/ --strict --explicit-package-bases
