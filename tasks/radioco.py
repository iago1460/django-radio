from invoke import task, call, Collection
from docker import build, setup, run, manage


@task(
    pre=[build, setup, call(run, background=True)],
    post=[call(manage, management_command='create_example_data')]
)
def quickstart(ctx):
    print('RadioCo should be running now')
    print('Generating some data...')


@task
def commit_changes(ctx):
    # Add files
    ctx.run('git add .')
    # Add local settings excluded on gitignore
    ctx.run('git add -f radioco/configs/base/local_settings.py')
    ctx.run('git add -f radioco/configs/development/local_settings.py')
    ctx.run('git add -f radioco/configs/heroku/local_settings.py')
    # Commit all
    ctx.run('git commit -am "autocommit: save changes"')


@task
def checkout_latest(ctx):
    ctx.run('git pull')


# ns = Collection(commit_changes, checkout_latest)
