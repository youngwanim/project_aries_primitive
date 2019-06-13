import json
import os
import random

from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run


BASE_POSTFIX = '/base'

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = PROJECT_DIR + BASE_POSTFIX

# deploy.json load to env variable
with open(os.path.join(PROJECT_DIR, "deploy.json")) as f:
    deploy_env = json.loads(f.read())

REPO_URL = deploy_env['REPO_URL']
PROJECT_NAME = deploy_env['PROJECT_NAME']
DEPLOY_TARGET = deploy_env['DEPLOY_TARGET']
PROJECT_SETTING = deploy_env['PROJECT_SETTING']
REMOTE_HOST_SSH = deploy_env['REMOTE_HOST_SSH']
REMOTE_HOST = deploy_env['REMOTE_HOST']
REMOTE_USER = deploy_env['REMOTE_USER']
REMOTE_PASSWORD = deploy_env['REMOTE_PASSWORD']

# Fabric env setting
env.user = REMOTE_USER
username = env.user
env.hosts = [
    REMOTE_HOST_SSH,
]
env.password = REMOTE_PASSWORD
project_folder = '/home/{}/{}'.format(env.user, PROJECT_NAME)

# APT 설치 목록
apt_requirements = [
    'git',  # 깃
    'python3-dev',  # Python 의존성
    'python3-pip',  # PIP
    'python3-tk', # Matplot lib
    'build-essential',  # C컴파일 패키지
    'python3-setuptools',  # PIP
    'libmysqlclient-dev',  # MySql
    'libssl-dev',  # SSL
    'libxml2-dev',  # XML
]


def deploy():
    # site_folder = PROJECT_DIR
    site_folder = '/home/nexttf/workspace/python/test_project_aries'
    virtual_env_folder = site_folder + '/venv'
    _create_directory(site_folder)
    _get_latest_source(site_folder, DEPLOY_TARGET)
    _update_virtualenv(virtual_env_folder, site_folder)
    _update_database(site_folder, virtual_env_folder, PROJECT_SETTING, True)


def _create_directory(site_folder):
    if not exists(site_folder):
        run('mkdir -p {0}'.format(site_folder))


def _update_settings():
    settings_path = project_folder + '/config/settings/{}.py'.format(DEPLOY_TARGET)
    sed(settings_path, "DEBUG = True", "DEBUG = False")

    secret_key_file = project_folder + '/config/keys/{}/secret_key.py'.format(DEPLOY_TARGET)
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _get_latest_source(site_folder, branch):
    if exists(site_folder + '/.git'):
        run('cd {0} && git pull origin {1}'.format(site_folder, branch))
    else:
        run('git clone {0} {1}'.format(REPO_URL, site_folder))

    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd {0} && git reset --hard {1}'.format(site_folder, current_commit))


def _update_virtualenv(venv_folder, site_folder):
    if not exists(venv_folder):
        run('cd {0} && python3 -m venv venv'.format(site_folder))

    run('{0}/venv/bin/pip3 install --upgrade pip'.format(site_folder))
    run('{0}/venv/bin/pip3 install -r {1}/requirements/base.txt'.format(site_folder, site_folder))


def _update_static_files(site_folder, virtualenv_folder):
    run('cd {0} && {1}/bin/python manage.py collectstatic --noinput'.format(site_folder, virtualenv_folder))


def _update_database(site_folder, virtualenv_folder, setting_param, cn_database):
    run('cd {0} && {1}/bin/python manage.py makemigrations --noinput --settings={2}'.format(
        site_folder, virtualenv_folder, setting_param
    ))

    run('cd {0} && {1}/bin/python manage.py migrate --noinput --settings={2}'.format(
        site_folder, virtualenv_folder, setting_param
    ))

    if cn_database:
        run('cd {0} && {1}/bin/python manage.py migrate --database=aries_cn --noinput --settings={2}'.format(
            site_folder, virtualenv_folder, setting_param
        ))
