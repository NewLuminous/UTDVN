# Use python:3.8 as the base Docker image
FROM python:3.8
# Set current working directory in the container
WORKDIR /home/utdvn
# Copy requirements into the docker container
COPY requirements.txt ./
# Install required Python packages
RUN pip install -r requirements.txt
# Copy the contents of the current working directory to the container
COPY . .
# Fix outdated Haystack ('django.utils.six' module was removed from django-3.0 onwards, use 'six' instead)
# Will be removed when future versions of django-haystack support Django 3.0
COPY fixs/web_haystack/backends__init__.py /usr/local/lib/python3.8/site-packages/haystack/backends/__init__.py
COPY fixs/web_haystack/solr_backend.py /usr/local/lib/python3.8/site-packages/haystack/backends/solr_backend.py
COPY fixs/web_haystack/highlight.py /usr/local/lib/python3.8/site-packages/haystack/templatetags/highlight.py
COPY fixs/web_haystack/utils__init__.py /usr/local/lib/python3.8/site-packages/haystack/utils/__init__.py
COPY fixs/web_haystack/loading.py /usr/local/lib/python3.8/site-packages/haystack/utils/loading.py
COPY fixs/web_haystack/inputs.py /usr/local/lib/python3.8/site-packages/haystack/inputs.py
COPY fixs/web_haystack/models.py /usr/local/lib/python3.8/site-packages/haystack/models.py
COPY fixs/web_haystack/query.py /usr/local/lib/python3.8/site-packages/haystack/query.py