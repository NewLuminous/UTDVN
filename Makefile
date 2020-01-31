.PHONY: all

build:
	docker-compose build

up:
	docker-compose up -d db phpmyadmin solr

dev:
	docker-compose run --rm -p 8000:8000 web python3 UTDVN_backend/manage.py runserver 0.0.0.0:8000

down:
	docker-compose down