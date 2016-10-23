from collections import namedtuple
from contextlib import contextmanager

import re
from fabric.api import env, local, require
from fabric.context_managers import lcd, prefix
from pip.req import parse_requirements
import os

from fab_utils import lsudo

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
HOME_DIR = os.path.expanduser('~')

env.heroku_project_name = 'radioco'
env.python = 'python2.7'
env.heroku_config_path = 'radio/configs/heroku'
env.environment = 'base'
# env.shell = '/bin/bash -c'


def quickstart():
    local('npm install bower')  # UBUNTU FIX: sudo apt-get install nodejs-legacy
    local('python manage.py bower install')
    local('python manage.py migrate')
    local('python manage.py create_example_data')
    local('python manage.py runserver')


def master():
    env.branch = 'master'


def branch(branch_name):
    env.branch = branch_name


def checkout_latest():
    local('git pull')


def heroku_setup():
    local('heroku login')
    local('heroku create %(heroku_project_name)s' % env)
    local('git init')
    local('heroku git:remote -a %(heroku_project_name)s' % env)


def save_changes():
    # Add files
    local('git add .')
    # Add local settings excluded on gitignore
    local('git add -f radio/configs/base/local_settings.py')
    local('git add -f radio/configs/development/local_settings.py')
    local('git add -f radio/configs/heroku/local_settings.py')
    # Commit all
    local('git commit -am "autocommit: save changes"')


def heroku_deploy():
    # Require branch
    require('branch', provided_by=[master, branch])
    # Deploy changes
    local('git push heroku %(branch)s' % env)
    # Install requirements and run migrations
    local('heroku run "python %(heroku_config_path)s/manage.py migrate"' % env)


# Docker
################

@contextmanager
def _generate_requirements_file():
    """
    pip version must be less than 1.6 (python 2 only)
    """
    requirements_path = os.path.join(env.environment_config, 'requirements.txt')
    tmp_requirement_path = os.path.join(env.environment_config, 'tmp_requirements.txt')
    requirements = [str(x.req or x.url) for x in parse_requirements(requirements_path)]
    with open(tmp_requirement_path, 'w+') as file:
        file.writelines('\n'.join(requirements))
    yield
    local('rm {environment_config}/tmp_requirements.txt'.format(**env))


@contextmanager
def _ssh_support():
    if os.path.isfile(os.path.join(HOME_DIR, '.ssh/id_rsa.pub')):
        local('cp ~/.ssh/id_rsa.pub {environment_config}/id_rsa.pub'.format(**env))
    else:
        local('touch {environment_config}/id_rsa.pub'.format(**env))
    yield
    local('rm {environment_config}/id_rsa.pub'.format(**env))


def _setup_development_environment():
    env.environment_config = os.path.join(BASE_DIR, 'radioco/configs/{environment}'.format(**env))
    with lcd(env.environment_config):
        local('chmod -R +x docker/scripts')

        env_variables = []
        env_file_path = os.path.join(env.environment_config, 'docker/env')
        local_env_file_path = os.path.join(env.environment_config, 'docker/local_env')
        if not os.path.exists(local_env_file_path):
            open(local_env_file_path, 'w').close()

        with open(env_file_path, 'r') as file:
            for line in file:
                cleaned_line = line.replace('\t', ' ').strip('\n ')
                if cleaned_line and not cleaned_line.startswith('#'):
                    export_var = '%s="%s"' % (line[:line.find('=')], line[line.find('=')+1:-1])
                    env_variables.append(export_var)

    return 'export %s' % ' '.join(env_variables)


def development():
    env.environment = 'development'


def setup_hosts(docker_machine=None):
    IP_ADDRESS_PATTERN = r'(?P<ip>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})'
    IP_ADDRESS = re.compile(IP_ADDRESS_PATTERN, flags=re.MULTILINE)
    HOST_LINE_PATTERN = re.compile(r'^\s*{IP_ADDRESS_PATTERN}\s+(?P<hostname>[\w\.\-_]+)'.format(IP_ADDRESS_PATTERN=IP_ADDRESS_PATTERN))
    HOST_LINE_FORMAT = '{ip}    {hostname}    # GENERATED AUTOMATICALLY'
    HOSTNAME = 'radioco'
    HostEntry = namedtuple('HostEntry', ['ip', 'hostname'])

    if docker_machine:
        machines = local('docker-machine ls | grep {machine}'.format(machine=docker_machine), capture=True)
    else:
        machines = local('docker-machine ls', capture=True)
    docker_machine_ips = tuple(match.group(1) for match in IP_ADDRESS.finditer(machines))
    if len(docker_machine_ips) != 1:
        if docker_machine:
            msg = 'You have {0} machines running with the same name'.format(len(docker_machine_ips)) if len(docker_machine_ips) else 'The machine "{0}" is not running'.format(docker_machine)
        else:
            msg = 'You have {0} machines running. Please specify a name'.format(len(docker_machine_ips)) if len(docker_machine_ips) else 'There are no machines running'
        raise RuntimeError(msg)
    docker_machine_ip = docker_machine_ips[0]

    with open('/etc/hosts', 'r') as hosts_filehandle:
        hosts_lines = hosts_filehandle.read().split('\n')

    host_line_exist = False
    new_host_lines = []
    for host_line in hosts_lines:
        try:
            host_entry = HostEntry(**HOST_LINE_PATTERN.match(host_line).groupdict())
        except AttributeError:
            new_host_lines.append(host_line)
        else:
            if host_entry.hostname == HOSTNAME:
                host_line_exist = True
                new_host_lines.append(HOST_LINE_FORMAT.format(ip=docker_machine_ip, hostname=HOSTNAME))
            else:
                new_host_lines.append(host_line)
    if not host_line_exist:
        new_host_lines.append(HOST_LINE_FORMAT.format(ip=docker_machine_ip, hostname=HOSTNAME))
        new_host_lines.append('')

    with open('/tmp/hosts', 'w') as hosts_filehandle:
        hosts_filehandle.write('\n'.join(new_host_lines))
    lsudo("sh -c 'cat /tmp/hosts > /etc/hosts'".format('\n'.join(new_host_lines)))


def docker_build():
    require('environment', provided_by=[development])
    with prefix(_setup_development_environment()):
        with lcd(env.environment_config), _generate_requirements_file(), _ssh_support():
            local('docker-compose build')


def docker_run(background=False):
    require('environment', provided_by=[development])
    with prefix(_setup_development_environment()):
        with lcd(env.environment_config), _generate_requirements_file(), _ssh_support():
            local('docker-compose up {0}'.format('-d' if background else ''))
            # local('docker-compose run --service-ports development_django')


def docker_stop():
    require('environment', provided_by=[development])
    with prefix(_setup_development_environment()):
        with lcd(env.environment_config):
            local('docker-compose stop')


def docker_clean():
    require('environment', provided_by=[development])
    with prefix(_setup_development_environment()):
        with lcd(env.environment_config):
            local('docker-compose down')

    # local('docker stop $(docker ps -a -q) || true')
    # local('docker rm $(docker ps -a -q) || true')


def docker_destroy():
    require('environment', provided_by=[development])
    with prefix(_setup_development_environment()):
        with lcd(env.environment_config):
            local('docker-compose down --rmi all')
            # local('docker-compose down --rmi local')

    # docker_clean()
    # local('docker rmi --force $(docker images -q)')
