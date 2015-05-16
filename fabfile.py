from fabric.api import env, local, require, lcd


env.project_name = 'radioco'
env.python = 'python2.7'

def heroku_setup():
    local('heroku login')
    local('heroku create %(project_name)s' % env)
    local('git init')
    local('heroku git:remote -a %(project_name)s' % env)


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