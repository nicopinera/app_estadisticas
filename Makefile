instalar_dependencias_w:
	@echo "Instalando dependencias para windows..."
	python -m pip install --upgrade pip;\
	pip install -r requerimientos.txt

instalar_dependencias_l:
	@echo "Instalando dependencias para linux..."

run_test:
	@echo "Ejecutando test...";
	pytest -v --cov=src --cov-report=html