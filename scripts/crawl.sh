#!/bin/bash

usage="
  Usage: `basename $0` [-h] [-t n]
  where:
    -h    show help text
    -t    set how long to run spiders for (in seconds)
"

set -e

while getopts ':ht:' option; do
  case "$option" in
    h) echo "$usage"
       exit
       ;;
    t) time=$OPTARG
       ;;
    :) printf "  Missing argument for -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
   \?) printf "  Illegal option: -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
  esac
done

cd UTDVN_crawler
if [ "$time" ]; then
  python crawler.py & read -t $time ; kill $!
  echo 'Crawler run for ' $time ' seconds'
else
  python crawler.py
fi