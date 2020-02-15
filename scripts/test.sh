#!/bin/bash

set -e

python UTDVN_backend/manage.py test UTDVN_backend UTDVN_crawler --config=.coveragerc
coverage report -m