# UTDVN :mag_right: :book:
[![Build Status](https://api.travis-ci.org/newluminous/UTDVN.svg)](https://travis-ci.org/newluminous/UTDVN)
[![Coverage Status](https://coveralls.io/repos/github/NewLuminous/UTDVN/badge.svg?branch=dev)](https://coveralls.io/github/NewLuminous/UTDVN)

Search engine service backed by Apache Solr, Django and Scrapy for undergraduate theses and dissertations

## Table of contents

* [Useful Links](#useful-links)
* [Installation](#installation)
* [Usage](#usage)
  * [Accessing Django](#accessing-django)
  * [Accessing Solr](#accessing-solr)
  * [Adding data to Solr to search in](#adding-data-to-solr-to-search-in)
* [Testing](#testing)

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

- When all containers are ready you can get bash into your `web` container
```Shell
$ docker-compose exec web bash
```

- Create a Django admin user
```Shell
$ docker-compose exec web python3 UTDVN_backend/manage.py createsuperuser
```

## Usage

### Accessing Django
- Go to http://localhost:8000
- To access your Django admin interface, go to http://localhost:8000/admin
- To test the backend API, go to http://localhost:8000/api/[ENDPOINT]/?[PARAMS]

### Accessing Solr
- To access your Solr admin interface, go to http://localhost:8983/solr
- To query a core named "test", go to http://localhost:8983/solr/#/test/query

### Adding data to Solr to search in
```Shell
$ docker-compose exec web bash scripts/crawl.sh
```

or just (if possible)
```Shell
$ bash scripts/crawl.sh
```

## Testing

- To populate the "test" core in Solr with test data:
```Shell
$ docker-compose exec solr post -c test opt/solr/example/exampledocs
```

- To empty a core:
```Shell
$ docker-compose exec solr post -c [CORE NAME] -d "<delete><query>*:*</query></delete>"
```
