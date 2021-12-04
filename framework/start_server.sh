#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
mkdir /ctf
mkdir /ctf/ctf
mkdir /ctf/logs
cp -r $DIR/ctfhost/files /ctf/ctf
cp -r $DIR/ctfhost/logs /ctf/ctf/files/logs
source /ctf/ctf/files/venv/bin/activate
pip install flask
pip install -r /ctf/ctf/files/requirements.txt
export FLASK_APP=/ctf/ctf/files/scoreboard.py
export FLASK_ENV=development
cd /
./ctf/ctf/files/scoreboard.py
