#!/bin/bash
# Waits until services have booted then migrate and boot Django server

bash scripts/wait.sh "Solr" "curl -s solr:8983/solr"
python scripts/nltk_setup.py
python UTDVN_backend/manage.py makemigrations
python UTDVN_backend/manage.py migrate
python UTDVN_backend/manage.py runserver 0.0.0.0:8000