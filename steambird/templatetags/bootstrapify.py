"""
Filter to bootstrapify Django template form-tags
"""
from django import template
from django.utils.safestring import mark_safe

# pylint: disable=invalid-name
register = template.Library()


@register.filter(name='form_bootstrapify', is_safe=True)
def form_bootstrapify(formfield_html):
    label_txt = str(formfield_html.label)
    formfield_html = str(formfield_html)

    if any(["type=\"{}\"".format(x) in formfield_html
            for x in ["text", "url", "email", "password"]]) or \
        any(["</{}>".format(x) in formfield_html
             for x in ["textarea", "select"]]):

        formfield_html = formfield_html.replace(
            "id=", "class=\"form-control\" id=")
        formfield_html = formfield_html.replace(
            "id=", "placeholder=\"{}\" id=".format(label_txt))

    return mark_safe(formfield_html)
