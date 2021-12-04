#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
docker-compose -f $DIR/ctf.yml build ctfdb && docker-compose -f $DIR/ctf.yml up
