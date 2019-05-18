from django import template
from django.template.loader import get_template

from steambird.models_materials import StudyMaterialEdition

# pylint: disable=invalid-name
register = template.Library()


@register.simple_tag(takes_context=True)
def render_template_type(_context,
                         obj: StudyMaterialEdition,
                         template_path: str):

    material_object = obj.polymorphic_ctype.model

    return get_template(
        template_path.format(material_object)
    ).render({material_object: obj})
