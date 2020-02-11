#!/bin/bash

set -e

python UTDVN_backend/manage.py test UTDVN_backend UTDVN_crawler
coverage report -m --omit='*/tests.py','*/apps.py','*/middlewares.py','*/settings.py','*/crawler.py'