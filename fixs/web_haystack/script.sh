#!/bin/sh
cp -f ./fixs/web_haystack/backends__init__.py /home/travis/virtualenv/python3.8.0/lib/python3.8/site-packages/haystack/backends/__init__.py
cp -f ./fixs/web_haystack/solr_backend.py /home/travis/virtualenv/python3.8.0/lib/python3.8/site-packages/haystack/backends/solr_backend.py
cp -f ./fixs/web_haystack/highlight.py /home/travis/virtualenv/python3.8.0/lib/python3.8/site-packages/haystack/templatetags/highlight.py
cp -f ./fixs/web_haystack/utils__init__.py /home/travis/virtualenv/python3.8.0/lib/python3.8/site-packages/haystack/utils/__init__.py
cp -f ./fixs/web_haystack/loading.py /home/travis/virtualenv/python3.8.0/lib/python3.8/site-packages/haystack/utils/loading.py
cp -f ./fixs/web_haystack/inputs.py /home/travis/virtualenv/python3.8.0/lib/python3.8/site-packages/haystack/inputs.py
cp -f ./fixs/web_haystack/models.py /home/travis/virtualenv/python3.8.0/lib/python3.8/site-packages/haystack/models.py
cp -f ./fixs/web_haystack/query.py /home/travis/virtualenv/python3.8.0/lib/python3.8/site-packages/haystack/query.py