from django.conf import settings


def global_vars(request):
    return {'SITE_NAME': settings.SITE_NAME}
