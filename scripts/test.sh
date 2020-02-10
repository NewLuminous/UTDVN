#!/bin/bash

cd UTDVN_backend
python manage.py test
coverage report -m --omit='*/tests.py','*/apps.py'