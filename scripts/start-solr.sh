#!/bin/bash

set -e

echo "Starting Solr"

solr -f &
bash create-cores.sh $@ &
wait
bash schema-api.sh &
wait