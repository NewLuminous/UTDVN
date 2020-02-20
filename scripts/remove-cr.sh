#!/bin/bash
# Remove trailing \r character from the file

set -e
file=$1

if [ "$1" ]; then
  sed -i 's/\r$//' $file
else
  sed -i 's/\r$//' scripts/add-crawled-data.sh
  sed -i 's/\r$//' scripts/schema-api.sh
  sed -i 's/\r$//' scripts/crawl.sh
  sed -i 's/\r$//' scripts/create-cores.sh
  sed -i 's/\r$//' scripts/start-solr.sh
  sed -i 's/\r$//' scripts/start-web.sh
  sed -i 's/\r$//' scripts/test.sh
  sed -i 's/\r$//' scripts/wait.sh
fi