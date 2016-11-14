from invoke import task, Collection


@task(default=True)
def quickstart(ctx):
    ctx.run('npm install bower')  # UBUNTU FIX: sudo apt-get install nodejs-legacy
    ctx.run('python manage.py bower install')
    ctx.run('python manage.py migrate')
    ctx.run('python manage.py create_example_data')
    ctx.run('python manage.py runserver')


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
