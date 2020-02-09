#!/bin/bash
# Remove trailing \r character from the file

set -e
file=$1

sed -i 's/\r$//' $file