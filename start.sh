#!/bin/bash
# source /home/comarch/Desktop/BIT/venv/bin/activate 
export FLASK_ENV=development
export FLASK_APP=web
rm admin.sqlite
rm user.sqlite
flask init-user-db
flask init-admin-db
flask run --host 0.0.0.0
