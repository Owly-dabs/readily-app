load-env:
	@echo "Loading environment variables from .env..."
	@export $$(grep -v '^#' .env | xargs) && \
	echo "Environment variables loaded."
install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
install-uv:
		uv pip install -r requirements.txt
format:
	# format code
	black *.py */*.py
lint:
	# flake8 or pylint
	pylint --disable=R,C,E0401 --ignore=streamlit_app.py *.py
test:
	# test
	# 	python -m pytest -vv --cov=mylib test_*.py
build:
	# build container
	docker build -t readily-api .
run:
	# run container
	docker run -p 127.0.0.1:8080:8080 readily-api:latest
deploy:
	# deploy
	docker build -t readily-api .
	docker tag readily-api:latest owlydabs/readily:latest
	docker push owlydabs/readily:latest

all: install lint test deploy