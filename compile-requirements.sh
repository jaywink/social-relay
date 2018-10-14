#!/usr/bin/env bash

export CUSTOM_COMPILE_COMMAND='./compile-requirements.sh'

pip-compile requirements/requirements.in $1 $2 $3
pip-compile requirements/postgresql.in $1 $2 $3
pip-compile requirements/mysql.in $1 $2 $3
pip-compile requirements/development.in $1 $2 $3
