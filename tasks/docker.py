from contextlib import contextmanager
from functools import wraps

from invoke import task, Collection

from pip.req import parse_requirements
import os

from utils import setup_host

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
HOME_DIR = os.path.expanduser('~')


@contextmanager
def chdir(dirname=None):
    """
    Not safe running concurrence tasks
    """
    current_dir = os.getcwd()
    os.chdir(dirname)
    yield
    os.chdir(current_dir)


@contextmanager
def _generate_requirements_file(ctx):
    """
    pip version must be less than 1.6 (python 2 only)
    """
    requirements_path = os.path.join(ctx['env_path'], 'requirements.txt')
    tmp_requirement_path = os.path.join(ctx['env_path'], 'tmp_requirements.txt')
    requirements = [str(x.req or x.url) for x in parse_requirements(requirements_path)]
    with open(tmp_requirement_path, 'w+') as file:
        file.writelines('\n'.join(requirements))
    yield
    ctx.run('rm {env_path}/tmp_requirements.txt'.format(**ctx))


@contextmanager
def _ssh_support(ctx):
    if os.path.isfile(os.path.join(HOME_DIR, '.ssh/id_rsa.pub')):
        ctx.run('cp ~/.ssh/id_rsa.pub {env_path}/id_rsa.pub'.format(**ctx))
    else:
        ctx.run('touch {env_path}/id_rsa.pub'.format(**ctx))
    yield
    ctx.run('rm {env_path}/id_rsa.pub'.format(**ctx))


def _setup_environment(ctx):
    ctx['env_path'] = os.path.join(BASE_DIR, 'radioco/configs/{environment}'.format(**ctx))
    ctx.run('chmod -R +x {env_path}/docker/scripts'.format(**ctx))

    env_file_path = os.path.join(ctx['env_path'], 'docker/env')
    local_env_file_path = os.path.join(ctx['env_path'], 'docker/local_env')
    if not os.path.exists(local_env_file_path):
        open(local_env_file_path, 'w').close()

    env_vars = {}
    with open(env_file_path, 'r') as file:
        for line in file:
            cleaned_line = line.replace('\t', ' ').strip('\n ')
            if cleaned_line and not cleaned_line.startswith('#'):
                spliter_index = cleaned_line.find('=')
                env_vars[cleaned_line[:spliter_index]] = cleaned_line[spliter_index+1:]

    return env_vars


def setup_env(func):
    @wraps(func)
    def func_wrapper(ctx, environment=None):
        ctx['environment'] = environment or ctx['environment']
        env_vars = _setup_environment(ctx)
        return func(ctx, env_vars)
    return func_wrapper


@task(default=True)
@setup_env
def build(ctx, env_vars):
    with _generate_requirements_file(ctx), _ssh_support(ctx):
        with chdir(ctx['env_path']):
            ctx.run('docker-compose build', env=env_vars)


@task
def run(ctx, environment=None, background=None):
    ctx['environment'] = environment or ctx['environment']
    env_vars = _setup_environment(ctx)
    with _generate_requirements_file(ctx), _ssh_support(ctx):
        with chdir(ctx['env_path']):
            ctx.run('docker-compose up {0}'.format('-d' if background else ''), env=env_vars)


@task
@setup_env
def shell(ctx, env_vars):
    with chdir(ctx['env_path']):
        ctx.run('docker-compose exec {image} {command}'.format(
            image='{environment}_django'.format(**ctx),
            # command='cat /srv/docker-dev/docker/scripts_container/_shell_environment.sh && /bin/bash'), pty=True)
            command='/bin/bash -c "cd /radioco/{path} && /bin/bash"'.format(path=ctx['env_path'].replace(BASE_DIR, ''))),
            env=env_vars,
            pty=True)


@task
@setup_env
def stop(ctx, env_vars):
    with chdir(ctx['env_path']):
        ctx.run('docker-compose stop', env=env_vars)


@task
@setup_env
def clean(ctx, env_vars):
    with chdir(ctx['env_path']):
        ctx.run('docker-compose down', env=env_vars)


@task
@setup_env
def destroy(ctx, env_vars):
    with chdir(ctx['env_path']):
        ctx.run('docker-compose down --rmi all', env=env_vars)


ns = Collection(build, run, shell, stop, clean, destroy)
ns.add_task(setup_host)
ns.configure({'environment': 'development'})
