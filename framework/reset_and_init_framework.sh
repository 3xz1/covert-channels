#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -n "Are you sure? This will delete everything!(y/n)? "
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    rm -rf /ctf/*
    docker-compose -f $DIR/ctf.yml rm -f ctfdb && docker-compose -f $DIR/ctf.yml build
fi
