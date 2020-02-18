.PHONY: all

build:
	docker-compose build

up:
	docker-compose up -d db solr

dev:
	docker-compose run --rm --name utdvn_web -p 8000:8000 web

down:
	docker-compose down

bash:
	docker exec -it utdvn_web bash

migrate:
	docker exec -it utdvn_web python3 UTDVN_backend/manage.py makemigrations
	docker exec -it utdvn_web python3 UTDVN_backend/manage.py migrate

create_core:
	docker-compose exec solr solr create_core -c $(CORE_NAME)

populate:
	docker-compose exec solr post -c test example/exampledocs

empty_core:
	docker-compose exec solr post -c $(CORE_NAME) -d "<delete><query>*:*</query></delete>"

start_solr:
	docker-compose exec solr solr create_core -c test
	docker-compose exec solr post -c test example/exampledocs
