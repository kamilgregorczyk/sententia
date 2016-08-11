from fabric.api import run, local
from fabric.api import env
from fabric.context_managers import cd

env.user = 'uniqe15'
env.hosts = ['s8.mydevil.net']
PROJECT_PATH = '/usr/home/uniqe15/domains/sententia.uniqe15.usermd.net/public_python'
venv_path = '/usr/home/uniqe15/.virtualenvs/sententia/bin/python'

def deploy():
    run('export DJANGO_SETTINGS_MODULE=sententia.production')
    run('cd %s; git pull' % PROJECT_PATH)
    run('%s %s/manage.py migrate' % (venv_path, PROJECT_PATH))
    run('%s %s/manage.py collectstatic --noinput' % (venv_path, PROJECT_PATH))
    run('devil www restart sententia.uniqe15.usermd.net')
