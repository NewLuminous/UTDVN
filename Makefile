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
    
crawl:
	docker exec -it utdvn_web bash scripts/crawl.sh

empty_core:
	docker-compose exec solr post -c $(CORE_NAME) -d "<delete><query>*:*</query></delete>"
    
test:
	docker exec -it utdvn_web bash scripts/test.sh
