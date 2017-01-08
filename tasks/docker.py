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


@task
@set_env
def setup(ctx):
    # Build images
    with _generate_requirements_file(ctx):
        if ctx['environment'] == 'development':
            # Copying ssh key to allow remote debugging
            with _ssh_support(ctx):
                ctx.run('docker-compose build')
        else:
            ctx.run('docker-compose build')

    # Start containers
    ctx.run('docker-compose up -d --no-recreate --no-build')

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
def start(ctx, environment=None, daemon=True):
    """
    This command will start the containers
    """
    ctx = _set_env(ctx, environment)
    with chdir(ctx['env_path']):
        # --no-recreate --no-build avoid rebuilding or building the image
        ctx.run('docker-compose up {} --no-recreate --no-build'.format('-d' if daemon else ''))


@task
@set_env
def stop(ctx):
    ctx.run('docker-compose stop')


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
def ssh(ctx):
    # WARNING: Control+C is not being handle properly? looks fixed on version 0.14.0
    ctx.run(
        'docker-compose exec {image} {command}'.format(
            image=_get_service_name(ctx),
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
                service=_get_service_name(ctx, service_name)  # service is always required
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
def clean(ctx):
    """
    Use this command to remove the containers.
    The data stored in the database will survive.
    """
    ctx.run('docker-compose down')


@task
@set_env
def destroy(ctx):
    """
    Use this command to remove the containers, the volumes and the images
    WARNING: This command will remove all your data
    """
    ctx.run('docker-compose down --rmi all')
    ctx.run('docker-compose down --volumes')
