#!/bin/bash

if [[ ! -d static/pictures ]]
then
    mkdir static/pictures
fi
python3 scripts/init_database.py
python3 scripts/init_post.py
python3 scripts/create_relations.py
