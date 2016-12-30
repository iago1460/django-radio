import os
import re
import tempfile

from invoke import task, UnexpectedExit
from .utils import BASE_DIR, commit_settings, run_ignoring_failure, chdir

PYTHON = 'python-2.7'
POSTGRES = 'postgresql-9.2'
OPENSHIFT_CONFIG_PATH = 'radioco/configs/openshift/'


@task()
def install_requirements(ctx):
    """
    Install local requirements
    """
    ctx.sudo('apt-get update')
    ctx.sudo('apt-get install git-core')
    ctx.sudo('gem install rhc')
    # Installing bower
    run_ignoring_failure(ctx.sudo, 'apt-get install nodejs')
    run_ignoring_failure(ctx.sudo, 'apt-get install nodejs-legacy')
    ctx.sudo('apt-get install npm')
    ctx.run('npm install bower')


@task()
def setup(ctx, project_name='radioco'):
    """
    This method will setup the repo in a new branch called openshift
    Requirements: cp, git, rhc, bower
    """
    # Setting up project
    ctx.run('rhc setup', pty=True)
    ctx.run('rhc app create {name} {python} --no-git'.format(name=project_name, python=PYTHON))
    ctx.run('rhc cartridge add {postgres} -a {name}'.format(name=project_name, postgres=POSTGRES))
    # Working in a temporal directory
    tmp_path = tempfile.mkdtemp()
    ctx.run('cp -R {repo_path} {tmp_path}'.format(
        repo_path=os.path.join(BASE_DIR, '.'),
        tmp_path=tmp_path)
    )
    with chdir(tmp_path):
        # Copying required files to project root
        ctx.run('cp -Rf {source_path} {tmp_path}'.format(
            source_path=os.path.join(tmp_path, OPENSHIFT_CONFIG_PATH, 'root/.'),
            tmp_path=tmp_path)
        )
        # Downloading bower dependencies
        ctx.run('node_modules/bower/bin/bower install')
        ctx.run('git add -f .openshift wsgi requirements.txt radioco/apps/radioco/static/bower')
        commit_settings(ctx, 'Autocommit: Openshift setup', dir_name=tmp_path, environment='openshift')
        # Getting remote git url
        openshift_info = ctx.run('rhc app-show -v -a {}'.format(project_name))
        try:
            git_url = re.search(r'Git URL:(.+)', openshift_info.stdout).group(1).strip()
        except AttributeError:
            raise RuntimeError('Failed to get git url')
        # Setting remote branch
        try:
            ctx.run('git remote add openshift {}'.format(git_url))
        except UnexpectedExit:
            ctx.run('git remote set-url openshift {}'.format(git_url))
        # Sending content to server
        ctx.run('git push -f openshift openshift:master')


@task
def ssh(ctx, project_name='radioco'):
    ctx.run('rhc ssh -a {}'.format(project_name), pty=True)


@task
def logs(ctx, project_name='radioco'):
    ctx.run('rhc tail -a {}'.format(project_name), pty=True)


@task
def start(ctx, project_name='radioco'):
    ctx.run('rhc app start -a {}'.format(project_name))


@task
def stop(ctx, project_name='radioco'):
    ctx.run('rhc app stop -a {}'.format(project_name))


@task
def restart(ctx, project_name='radioco'):
    ctx.run('rhc app stop -a {}'.format(project_name))
    ctx.run('rhc app start -a {}'.format(project_name))
