Hive
=============
Service for creating dynamic tables

Require
----------

- Python 3.10


Developing
----------

### Init environment ###

Execute command in project dir:

    docker-compose up --build

### Jwt public and private keys
The keys are generated using the following command:

    bash hive_project/create_jwt_keys.sh


### Change .env.example to .env and fill it with your data

    .env.example -> .env

### Make migrations ###

    docker compose run hive python manage.py migrate


### Run tests ###   

    docker-compose run hive python manage.py test

### Run server ###

    docker-compose run hive python manage.py runserver
    or
    docker-compose run hive

