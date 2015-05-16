from fabric.api import env, local, require, lcd


env.heroku_project_name = 'radioco'
env.python = 'python2.7'
env.heroku_config_path = 'radio/configs/heroku'

def heroku_setup():
    local('heroku login')
    local('heroku create %(heroku_project_name)s' % env)
    local('git init')
    local('heroku git:remote -a %(heroku_project_name)s' % env)
    local('heroku ps:scale web=1')

def commit_change

def master():
    """
    Work on master branch.
    """
    env.branch = 'master'


def commit():
    local('git add .')
    local('git commit -am "autocommit"')


def heroku_deploy():
    # Save current branch
    env.current_branch = local('git rev-parse --abbrev-ref HEAD', capture=True)

    # Change branch
    local('git checkout -b local_heroku')

    # Add local settings
    local('git add -f radio/configs/common/local_settings.py')
    local('git add -f radio/configs/development/local_settings.py')
    local('git add -f radio/configs/heroku/local_settings.py')
    local('git commit -m "autocommit: Added local_settings"')

    # Deploy changes
    local('git push heroku %(branch)s' % env)

    # Install requirements and run migrations
    local('heroku run "pip install -r %(heroku_config_path)s/requirements.txt"' % env)
    local('heroku run "python %(heroku_config_path)s/manage.py migrate"' % env)

    # Return current branch
    local('git checkout %(current_branch)s' % env)