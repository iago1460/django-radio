import tempfile
from contextlib import contextmanager
from invoke import UnexpectedExit
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
HOME_DIR = os.path.expanduser('~')


def run_ignoring_failure(method, command):
    try:
        method(command)
    except UnexpectedExit:
        pass


@contextmanager
def chdir(dirname=None):
    """
    Not safe running concurrence tasks
    """
    current_dir = os.getcwd()
    os.chdir(dirname)
    yield
    os.chdir(current_dir)

@contextmanager
def use_tmp_dir(ctx):
    """
    Not safe running concurrence tasks
    """
    tmp_path = tempfile.mkdtemp()
    ctx.run('cp -R {repo_path} {tmp_path}'.format(
        repo_path=os.path.join(BASE_DIR, '.'),
        tmp_path=tmp_path)
    )
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(current_dir)


def commit_settings(ctx, message, dir_name=None, environment='base'):
    with chdir(dir_name or BASE_DIR):
        run_ignoring_failure(ctx.run, 'git add -f radioco/configs/base/local_settings.py')
        if environment != 'base':
            run_ignoring_failure(ctx.run, 'git add -f radioco/configs/{}/local_settings.py'.format(environment))
        run_ignoring_failure(ctx.run, 'git commit -am "{}"'.format(message))


def get_current_branch(ctx):
    return ctx.run('git rev-parse --abbrev-ref HEAD').stdout.strip()


# @contextmanager
# def change_branch(ctx, branch=None):
#     """
#     Change to other branch temporally if a branch is provided
#     """
#     current_branch = ctx.run('git rev-parse --abbrev-ref HEAD').stdout
#     if branch:
#         ctx.run('git checkout {}'.format(branch))
#     yield
#     ctx.run('git checkout {}'.format(current_branch))


def _read_requirements_file(filename, parent=None):
    parent = (parent or __file__)
    try:
        with open(os.path.join(os.path.dirname(parent), filename)) as f:
            return f.read()
    except IOError:
        return ''


def parse_requirements(filename, parent=None):
    parent = (parent or __file__)
    filepath = os.path.join(os.path.dirname(parent), filename)
    content = _read_requirements_file(filename, parent)

    for line_number, line in enumerate(content.splitlines(), 1):
        candidate = line.strip()

        if candidate.startswith('-r'):
            for item in parse_requirements(candidate[2:].strip(), filepath):
                yield item
        else:
            yield candidate