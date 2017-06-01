from django.conf import settings
from django.test.runner import DiscoverRunner


class MyTestSuiteRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        settings.TESTING_MODE = True
        super(MyTestSuiteRunner, self).__init__(*args, **kwargs)
