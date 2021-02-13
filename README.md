# system-sandbox
This is a development repo for résumé auto-rater system, testing new features.
推免系统网站开发沙盒，先在这里随便搞，之后再建正式仓库
![CodeQL](https://github.com/NKDACS/system-sandbox/workflows/CodeQL/badge.svg)

## Installation Guide
### Prerequisite
- python 3.7+
- redis
- memcached(depreacated)
### Setup Python Virtual Environment
You may need to change your pypi source
```shell
# using 
pip install pipenv
# enter project directory
cd xxx
# install dependencies
pipenv install -r requirement.txt
# activate python virtual env
pipenv shell
```
**NOTE**: when debugging on **Windows**, delete `uwsgi` from `requirement.txt`
### Complete `secret.py`
create a `secret.py` containing the passwords and secret keys using the template `secret.py.example`
### Django Setup
```shell
# create database
python manage.py makemigrations
python manage.py migrates
# create superuser
python manage.py createsuperuser --username=foo --email=foo@bar.com
```
You may need to create `db.sqlite3` if you don't copy it from your debugging environment.
### Debug
1. set `DEBUG` variable in `system/settings.py` to **True**
2. run `python manage.py runserver`
### Deploy
uwsgi + nginx
1. change `DEBUG` variable in `system/settings.py` from **True** to **False**
2. copy `51datajobs.conf` to your nginx server configuration folder. (`/etc/nginx/conf.d/` or `/etc/nginx/sites-enabled/`)
3. install **uwsgi** and run `uwsgi --ini uwsgi.ini` (check `uwsgi.ini` in advance to make sure the relevant folders are created)

## TODOs
- [ ] student list view
- [ ] further develop the Resume fields and input format for ML models
- [ ] redis(seems not working) and cache
- [ ] UI design and frontend optimization
    (if neccessary, change to Vue.js and restful APIs)
- [ ] ...