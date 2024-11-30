# from django.views.debug import get_safe_settings
from django.conf import settings


def settings(request):
    # settings_py = get_safe_settings()
    return {
        # 'settings': settings_py,
        'settings': settings.__dict__,
    }
