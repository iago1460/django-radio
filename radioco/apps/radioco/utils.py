from django.http import HttpResponseForbidden
from django.views.generic.detail import SingleObjectMixin


def create_example_data():
    from django.contrib.auth.models import User
    from radioco.apps.global_settings.models import SiteConfiguration
    from radioco.apps.radioco.test_utils import create_test_data

    # Create administrator
    user, created = User.objects.get_or_create(
        username='admin', defaults={
            'is_superuser': True,
            'is_staff': True,
        }
    )
    if created:
        user.set_password('1234')
        user.save()

    # Site config
    site_config = SiteConfiguration.get_global()
    site_config.about_footer = '''
        RadioCo is a broadcasting radio recording scheduling system.
        RadioCo has been intended to provide a solution for a wide range of broadcast projects,
        from community to public and commercial stations.
    '''
    site_config.more_about_us = 'Live shows are recorded and published automatically'
    site_config.address = 'http://radioco.org/'
    site_config.facebook_address = 'https://facebook.com/radioco.org'
    site_config.twitter_address = 'https://twitter.com/RadioCo_org'
    site_config.save()

    create_test_data()


class memorize(dict):
    """
    A simple cache system, use as decorator
    """
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.func(*key)
        return result


def field_has_changed(_object, field):
    return _object.id and getattr(_object.__class__.objects.get(id=_object.id), field) != getattr(_object, field)


def check_delete_permission(user, model):
    permission = '%s.%s' % (model._meta.app_label, "delete_%s" % model._meta.model_name)
    return user.has_perm(permission)


class DeletePermissionMixin(object):
    model = None

    def dispatch(self, request, *args, **kwargs):
        if not check_delete_permission(request.user, self.model):
            return HttpResponseForbidden("User doesn't have delete permission")
        return super(DeletePermissionMixin, self).dispatch(request, *args, **kwargs)


class GetObjectMixin(SingleObjectMixin):
    object = None

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super(GetObjectMixin, self).dispatch(*args, **kwargs)
