#!/bin/bash
# Wait until services have booted
# The first argument is the service's name
# The second argument is the condition

set -e

name=$1
condition=$2

echo >&2 "Waiting for $name"

while true; do
  if eval "$condition"; then
    break
  fi
  sleep 7
done

echo >&2 "$name is ready"