from contextlib import contextmanager
from functools import wraps

from invoke import task

import os
from .utils import chdir, HOME_DIR, BASE_DIR, parse_requirements


@contextmanager
def _generate_requirements_file(ctx):
    requirements_path = os.path.join(ctx['env_path'], 'requirements.txt')
    tmp_requirement_path = os.path.join(ctx['env_path'], 'tmp_requirements.txt')
    requirements = [_req for _req in parse_requirements(requirements_path)]
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


# def _setup_environment(ctx):
#     ctx['env_path'] = os.path.join(BASE_DIR, 'radioco/configs/{environment}'.format(**ctx))
#     ctx.run('chmod -R +x {env_path}/docker/scripts'.format(**ctx))
# 
#     env_file_path = os.path.join(ctx['env_path'], 'docker/env')
#     local_env_file_path = os.path.join(ctx['env_path'], 'docker/local_env')
#     if not os.path.exists(local_env_file_path):
#         open(local_env_file_path, 'w').close()
# 
#     env_vars = {}
#     with open(env_file_path, 'r') as file:
#         for line in file:
#             cleaned_line = line.replace('\t', ' ').strip('\n ')
#             if cleaned_line and not cleaned_line.startswith('#'):
#                 spliter_index = cleaned_line.find('=')
#                 env_vars[cleaned_line[:spliter_index]] = cleaned_line[spliter_index+1:]
# 
#     return env_vars


def _set_env(ctx, environment):
    ctx['environment'] = ctx.get('environment', environment) or 'base'
    ctx['env_path'] = os.path.join(BASE_DIR, 'radioco/configs/{environment}'.format(**ctx))
    return ctx


def _docker_compose_run(service_name, command):
    return 'docker-compose run --no-deps --rm {service} {command}'.format(service=service_name, command=command)


def _get_service_name(ctx, service=None):
    return '{environment}_{service}'.format(environment=ctx['environment'], service=service or 'django')


def set_env(func):
    @wraps(func)
    def func_wrapper(ctx, environment=None):
        ctx = _set_env(ctx, environment)
        with chdir(ctx['env_path']):
            return func(ctx)
    return func_wrapper


# Tasks

@task
@set_env
def build(ctx):
    with _generate_requirements_file(ctx):
        if ctx['environment'] == 'development':
            # Copying ssh key to allow remote debugging
            with _ssh_support(ctx):
                ctx.run('docker-compose build')
        else:
            ctx.run('docker-compose build')


@task
@set_env
def setup(ctx):
    # Adding executable permissions to docker scripts
    ctx.run('chmod -R +x {env_path}/docker/scripts'.format(**ctx))

    # Dependency services has to be running before start this service
    ctx.run(
        _docker_compose_run(
            _get_service_name(ctx),
            '/radioco/radioco/configs/{environment}/docker/scripts/setup.sh'.format(**ctx)
        )
    )


@task
def run(ctx, environment=None, daemon=True):
    """
    This command require to execute build first
    """
    ctx = _set_env(ctx, environment)
    with chdir(ctx['env_path']):
        # calling docker with --no-recreate --no-build to avoid rebuild or build the image
        ctx.run('docker-compose up {} --no-recreate --no-build'.format('-d' if daemon else ''))


@task
def manage(ctx, environment=None, command='help'):
    """
    Run manage.py management_command inside docker
    Args:
        command: management command

    """
    ctx = _set_env(ctx, environment)
    with chdir(ctx['env_path']):
        ctx.run(
            _docker_compose_run(
                _get_service_name(ctx),
                'bash -c "cd radioco && python {docker_path}/manage.py {command}"'.format(
                    docker_path='radioco/configs/{environment}'.format(**ctx),
                    command=command
                )
            ),
            pty=True
        )


@task
@set_env
def shell(ctx):
    # FIXME: Control+C is not being handle properly
    ctx.run(
        'docker-compose exec {image} {command}'.format(
            image='{environment}_django'.format(**ctx),
            # command='cat /srv/docker-dev/docker/scripts_container/_shell_environment.sh && /bin/bash'), pty=True)
            command='bash -c "cd /radioco/{path} && bash"'.format(path=ctx['env_path'].replace(BASE_DIR, ''))
        ), pty=True
    )


@task
@set_env
def attach(ctx, environment=None, service_name=None):
    ctx = _set_env(ctx, environment)

    with chdir(ctx['env_path']):
        ctx.run(
            'docker attach $(docker-compose ps -q {service})'.format(
                service=_get_service_name(ctx, service_name) # service is always required
            )
        )


@task
def logs(ctx, environment=None, service_name=None):
    ctx = _set_env(ctx, environment)

    with chdir(ctx['env_path']):
        ctx.run('docker-compose logs {service}'.format(
            service=_get_service_name(ctx, service_name) if service_name else '')
        )


@task
@set_env
def stop(ctx):
    ctx.run('docker-compose stop')


@task
@set_env
def clean(ctx):
    ctx.run('docker-compose down')


@task
@set_env
def destroy(ctx):
    ctx.run('docker-compose down --rmi all')
    ctx.run('docker-compose down --volumes')
