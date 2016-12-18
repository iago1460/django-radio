from django import template
from django.apps import apps

register = template.Library()

template_tag_name = 'get_global_model'


@register.assignment_tag(name=template_tag_name)
def get_global_model(model_path):
    try:
        app_label, model_name = model_path.rsplit('.', 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "Templatetag template_tag_name requires the following format: 'app_label.ModelName'. "
            "Received '%s'." % model_path
        )

    model_class = apps.get_model(app_label, model_name)
    if not model_class:
        raise template.TemplateSyntaxError(
            "Could not get the model name '%(model)s' from the application "
            "named '%(app)s'" % {
                'model': model_name,
                'app': app_label,
            }
        )
    return model_class.get_global()
