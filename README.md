# UTDVN :mag_right: :book:
[![Build Status](https://api.travis-ci.org/newluminous/UTDVN.svg)](https://travis-ci.org/newluminous/UTDVN)
[![Coverage Status](https://coveralls.io/repos/github/NewLuminous/UTDVN/badge.svg?branch=searcher)](https://coveralls.io/github/NewLuminous/UTDVN?branch=searcher)

Search engine service backed by Apache Solr, Django and Scrapy for undergraduate theses and dissertations

## Table of contents

* [Useful Links](#useful-links)
* [Installation](#installation)
* [Usage](#usage)
  * [Accessing Django](#accessing-django)
  * [Accessing Solr](#accessing-solr)
  * [Accessing phpMyAdmin](#accessing-phpMyAdmin)
* [Adding test data](#adding-test-data)

## Useful Links
[Getting Started with Docker](https://docs.docker.com/get-started/)<br/>
[Getting Started with Django](https://www.djangoproject.com/start/)<br/>
[Solr Tutorial](https://lucene.apache.org/solr/guide/8_4/solr-tutorial.html)<br/>
[Scrapy Video Tutorials](https://scrapinghub.com/learn-scrapy/)<br/>
[Getting Started with Haystack](https://django-haystack.readthedocs.io/en/master/tutorial.html)<br/>
[Travis CI Tutorial](https://docs.travis-ci.com/user/tutorial/)<br/>

## Installation
- Clone the project using git
```Shell
$ git clone https://github.com/NewLuminous/UTDVN.git
```

- [Install Docker](https://docs.docker.com/install/)<br/>
- Run
```Shell
$ docker-compose up
```

## Usage

Once containers have started you can `exec` into `bash` in your `web` container and configure a Django admin user.
```Shell
$ docker-compose exec web bash
# Create Django admin user
root@de5d08a4ea6e:/home/utdvn# python3 UTDVN_backend/manage.py createsuperuser
```

### Accessing Django
- Go to http://localhost:8000
- To access your Django admin interface, go to http://localhost:8000/admin

### Accessing Solr
- To access your Solr admin interface, go to http://localhost:8983/solr
- To query a core named "test", go to http://localhost:8983/solr/#/test/query

### Accessing phpMyAdmin
- To access your MySQL user interface, go to http://localhost:8888

## Adding test data

Once containers have started you can `exec` into `bash` in your `solr` container.
```Shell
$ docker-compose exec solr bash
# Populate the 'test' core with some test data
solr@c106f3a1a44c:/opt/solr-8.4.1$ post -c test example/exampledocs
```

- To empty a core:
```Shell
$ docker-compose exec solr post -c [CORE NAME] -d "<delete><query>*:*</query></delete>"
```
