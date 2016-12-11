from invoke import task, Collection

HEROKU_CONFIG_PATH = 'radioco/configs/heroku/'


@task(default=True)
def setup(ctx, project_name='radioco'):
    ctx.run('heroku login')
    ctx.run('heroku create {0}'.format(project_name))
    ctx.run('git init')
    ctx.run('heroku git:remote -a {0}'.format(project_name))


@task
def deploy(ctx, branch='master'):
    # Deploy changes
    ctx.run('git push heroku {0}'.format(branch))
    # Install requirements and run migrations
    ctx.run('heroku run "python {0}manage.py migrate"'.format(HEROKU_CONFIG_PATH))


ns = Collection(setup, deploy)
