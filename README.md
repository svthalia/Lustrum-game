# Thalia lustrum game
> This is the codebase for the game which will be played throughout the Thalia lustrum. It is made with Django and it uses Tailwindcss

[![Maintenance](https://img.shields.io/badge/Maintained%3F-until%20the%20lustrum-green.svg)]()
[![Biertje welcome](https://img.shields.io/badge/Biertje%3F-Offcourse!-brightgreen.svg?style=flat)]()


## Requirements  (Prerequisites)
Tools and packages required to successfully install this project.
For example:
* Linux or windows
* Python 3.9 and up
* NPM or Yarn

## Installation
A step by step list of commands / guide that informs how to install an instance of this project. 

`$ pip install pipenv`

`$ pipenv shell`

`$ pip install -r requirements.txt`

`$ python manage.py migrate `

`$ python manage.py runserver `

### In a separate terminal run

`$ pipenv shell`

`$ python manage.py tailwind install `

`$ python manage.py tailwind start `

## Deployment Notes

For Docker
```sh
docker compose build
```

```sh
docker compose up
```

```sh
docker-compose run web python3 manage.py migrate
```

```sh
docker-compose run web python3 manage.py tailwind build
```

## Authors 
Julian van der Horst  – julian "at" vdhorst "dot" dev
 
 You can find me here at:
[Github](https://github.com/Gulianrdgd)
