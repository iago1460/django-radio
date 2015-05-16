from fabric.api import env, local, require, lcd


env.heroku_project_name = 'radioco'
env.python = 'python2.7'
env.heroku_config_path = 'radio/configs/heroku'

def heroku_setup():
    local('heroku login')
    local('heroku create %(heroku_project_name)s' % env)
    local('git init')
    local('heroku git:remote -a %(heroku_project_name)s' % env)


def master():
    """
    Work on master branch.
    """
    env.branch = 'master'


def heroku_deploy():
    require('branch', provided_by=[master])

    # local('git add .')
    # local('git commit -am "autocommit to deploy"')

    local('git push heroku %(branch)s' % env)
    local('heroku run "pip install -r %(heroku_config_path)s/requirements.txt"' % env)
    local('heroku run "python %(heroku_config_path)s/manage.py migrate"' % env)