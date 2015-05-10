from fabric.api import env, local, require, lcd


env.project_name = 'django_radio'
env.python = 'python2.7'

def heroku_setup():
    local('heroku login')
    local('git init')
    local('heroku git:remote -a %(project_name)s' % env)

def production():
    """
    Work on production environment
    """
    pass


def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name


def heroku_deploy():
    require('settings', provided_by=[production])
    require('branch', provided_by=[branch])

    local('git add .')
    local('git commit -am "autocommit to deploy"')
    local('git push heroku %(branch)s' % env)