.PHONY: all

build:
	docker-compose build

up:
	docker-compose up -d db phpmyadmin solr

dev:
	docker-compose run --rm --name utdvn_web -p 8000:8000 web

down:
	docker-compose down

bash:
	docker exec -it utdvn_web bash

migrate:
	docker exec -it utdvn_web python3 UTDVN_backend/manage.py migrate