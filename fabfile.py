from fabric.api import env, local, require

env.heroku_project_name = 'radioco'
env.python = 'python2.7'
env.heroku_config_path = 'radio/configs/heroku'


def quickstart():
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
    local('git add -f radio/configs/common/local_settings.py')
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
