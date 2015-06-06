from django.views.debug import get_safe_settings

def settings(request):
    settings_py = get_safe_settings()
    return {
        'settings': settings_py,
    }
