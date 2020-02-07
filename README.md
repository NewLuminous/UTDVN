# UTDVN
[![Build Status](https://api.travis-ci.org/newluminous/UTDVN.svg)](https://travis-ci.org/newluminous/UTDVN)

Search engine service backed by Apache Solr, Django and Scrapy for undergraduate theses and dissertations

## Useful Links
[Getting Started with Docker](https://docs.docker.com/get-started/)<br/>
[Getting Started with Django](https://www.djangoproject.com/start/)<br/>
[Solr Tutorial](https://lucene.apache.org/solr/guide/8_4/solr-tutorial.html)<br/>
[Scrapy Video Tutorials](https://scrapinghub.com/learn-scrapy/)<br/>
[Getting Started with Haystack](https://django-haystack.readthedocs.io/en/master/tutorial.html)<br/>
[Travis CI Tutorial](https://docs.travis-ci.com/user/tutorial/)

## Installation
- Install Docker
- Run
```Shell
$ docker-compose up
```

- Once containers have started you can `exec` into `bash` in your `web` container and configure a Django admin user, or run migrations.
```Shell
$ docker-compose exec web bash
# Now you should be in the web container, cd into UTDVN_backend
root@de5d08a4ea6e:/home/utdvn# cd UTDVN_backend
# Run migrations
root@de5d08a4ea6e:/home/utdvn/UTDVN_backend# python3 manage.py migrate
# Create Django admin user
root@de5d08a4ea6e:/home/utdvn/UTDVN_backend# python3 manage.py createsuperuser
# Start Django server
root@de5d08a4ea6e:/home/utdvn/UTDVN_backend# python3 manage.py runserver 0.0.0.0:8000
```

### Accessing Django
- Go to http://localhost:8000
- To access your Django admin interface, go to http://localhost:8000/admin

### Accessing Solr
- To access your Solr admin interface, go to http://localhost:8983/solr
- To query a core named "test", go to http://localhost:8983/solr/#/test/query

### Accessing phpMyAdmin
- To access your MySQL user interface, go to http://localhost:8888

- To empty a core, go to:
```
http://localhost:8983/solr/[CORE NAME]/update?stream.body=<delete><query>*:*</query></delete>&commit=true
```
