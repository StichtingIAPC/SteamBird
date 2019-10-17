# SteamBird

[![Pipeline](https://git.iapc.utwente.nl/www/steambird/badges/master/pipeline.svg)](https://git.iapc.utwente.nl/www/steambird/pipelines)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg?logo=python)](https://www.python.org/downloads/release/python-370/)
[![Django 2.1](https://img.shields.io/badge/django-2.1-336f33.svg?logo=django)](https://docs.djangoproject.com/en/2.1/releases/2.1/)
[![Pipenv](https://img.shields.io/badge/pipenv-%E2%9C%94-brightgreen.svg)](https://pipenv.readthedocs.io/en/latest/)
[![GitLab](https://img.shields.io/badge/GitLab-IAPC-brightgreen.svg?logo=gitlab)](https://git.iapc.utwente.nl/www/steambird)

Project SteamBird. (SB) is a re-imagined version of the old ABC, for keeping track of StudyBooks

## Goal of this project

This project has as main goal to make the managing of book information within the University of Twente easier. It has been started as an in house development of 'Stichting IAPC', but might be licensed to other people later on. The main focus is the admin interface in which we have tried to create an as smooth as possible integration to quickly and easily add, update and manage information



## Getting your enviroment set up

To get started with working on this code, you will need to do some installation steps first.

 - Install Python 3.7, you can follow the link by clicking the badge above
   - On windows it is recommended to add python to the PATH, also make sure you install and accept this for pip (python's integrated package manager)
 -  Go to a shell and install pipenv by running: `pip install pipenv`
 - Optionally install pyenv, this is a python version management package. This is currently not recommended for Windows
 - Open a console/shell and run `pipenv --python 3.7`
 - Now we have created a pipenv enviroment, we can use all wonderful pipenv commands. Start by running: `pipenv sync -d` to install all packages for this project
 
## Starting up again

When you been away for a bit, it is thouroughly recommended to always pull and run `pipenv sync -d` to be most up to date with the current state of the project.


## Before you commit

Don't forget to run the pylint locally before committing, and especially a merge request! This is done (assuming you installed it using pipenv):
`pipenv run pylint steambird -dfixme` or, when doing this within a (pipenv) shell `pylint steambird -dfixme`. This will return a list of 'issues' as seen by the linter. Fix these before committing!
 