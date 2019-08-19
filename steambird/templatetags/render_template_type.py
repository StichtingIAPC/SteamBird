"""
Template tag library which resolves to include view based on Polymorphic Type of the material.
Currently unused
"""
from django import template
from django.template.loader import get_template

from steambird.models.materials import StudyMaterialEdition

# pylint: disable=invalid-name
register = template.Library()


@register.simple_tag(takes_context=True)
def render_template_type(_context, obj: StudyMaterialEdition, template_path: str):
    """
    Fetches template based on the type of the material. Works based on the Polymorphic c_type

    :param _context: Context of the page it is loaded from
    :param obj: StudyMaterialEdition object. Is used to retrieve the
    :param template_path: string to the relative path to find the template which should be rendered
    :return: template which is loaded
    """

    material_object = obj.polymorphic_ctype.model

    return get_template(
        template_path.format(material_object)
    ).render({material_object: obj})
