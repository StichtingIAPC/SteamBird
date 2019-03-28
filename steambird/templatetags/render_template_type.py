from django import template
from django.template.loader import get_template

register = template.Library()


@register.simple_tag(takes_context=True)
def render_template_type(context, obj, template_path: str):
    material_object = obj.polymorphic_ctype.model

    return get_template(
        template_path.format(material_object)
    ).render({material_object: obj})
