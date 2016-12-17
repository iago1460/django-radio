from contextlib import contextmanager
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
HOME_DIR = os.path.expanduser('~')


@contextmanager
def chdir(dirname=None):
    """
    Not safe running concurrence tasks
    """
    current_dir = os.getcwd()
    os.chdir(dirname)
    yield
    os.chdir(current_dir)


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