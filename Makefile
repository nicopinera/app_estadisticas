instalar_dependencias_w:
	@echo "Instalando dependencias para windows..."
	python -m pip install --upgrade pip
	pip install -r requerimientos.txt

instalar_dependencias_l:
	@echo "Instalando dependencias para linux..."

run_test:
	@echo "Ejecutando test..."
	pytest -v --cov=src --cov-report=html

run_linter_ruf:
	ruff check --select E --select I

corregir_linter:
	ruff check --fix --select E --select I . && ruff format .
	ruff check .

pre_commit:
	pip install pre-commit
	pre-commit
	pre-commit run --all-files

docker_test:
	docker build -f Dockerfile.test -t app-estadisticas-tests .
	docker run --rm app-estadisticas-tests

static_check:
	mypy src/ --strict --explicit-package-bases
