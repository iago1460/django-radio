import os
from invoke import task

from .utils import commit_settings, get_current_branch, use_tmp_dir, run_ignoring_failure

HEROKU_CONFIG_PATH = 'radioco/configs/heroku/'


@task()
def install_requirements(ctx):
    """
    Install heroku tool bar
    """
    ctx.sudo('add-apt-repository "deb https://cli-assets.heroku.com/branches/stable/apt ./"')
    ctx.run('curl -L https://cli-assets.heroku.com/apt/release.key | sudo apt-key add -')
    ctx.sudo('apt-get update')
    ctx.sudo('apt-get install heroku')
    print('Heroku requirements were installed correctly')


@task
def setup(ctx, project_name=''):
    run_ignoring_failure(ctx.run, 'git remote rm heroku')
    ctx.run('HEROKU_SSL_VERIFY=disable heroku login', pty=True)  # FIXME: insecure
    ctx.run('heroku create'.format(project_name))
    ctx.run('heroku config:set DISABLE_COLLECTSTATIC=1')
    ctx.run('heroku config:set DJANGO_SETTINGS_MODULE=radioco.configs.heroku.settings')
    ctx.run('heroku buildpacks:clear')
    ctx.run('heroku buildpacks:add heroku/nodejs')
    ctx.run('heroku buildpacks:add heroku/python')
    print('Heroku was setup correctly')


@task
def deploy(ctx):
    # Working in a temporal directory
    with use_tmp_dir(ctx) as tmp_path:
        # Copying required files to project root
        ctx.run('cp -Rf {source_path} {tmp_path}'.format(
            source_path=os.path.join(tmp_path, HEROKU_CONFIG_PATH, 'root/.'),
            tmp_path=tmp_path)
        )
        ctx.run('git add -f package.json Procfile requirements.txt')
        commit_settings(ctx, 'Autocommit: Heroku setup', dir_name=tmp_path, environment='heroku')
        ctx.run('git push -f heroku {current_branch}:master'.format(current_branch=get_current_branch(ctx)))
        # Install requirements and run migrations
        # ctx.run('heroku run "bower install && python manage.py collectstatic --noinput"')
        ctx.run('heroku run "python manage.py migrate"')
    print('Heroku was deployed correctly')


@task
def ssh(ctx):
    ctx.run('heroku run bash', pty=True)


@task
def logs(ctx):
    ctx.run('heroku logs')


@task
def manage(ctx, command='help'):
    """
    Run manage.py management_command
    """
    ctx.run('heroku run "python manage.py {}"'.format(command), pty=True)
