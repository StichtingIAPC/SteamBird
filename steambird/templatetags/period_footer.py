"""
A template tag which handles the query needed for the bottom_line footer, which shows the
current working period the site uses on some pages
"""
from django import template
from django.utils.translation import ugettext_lazy as _

from steambird.models.site_config import Config

# pylint: disable=invalid-name
register = template.Library()


@register.simple_tag()
def period_retrieval() -> str:
    """
    Template tag for retrieving the period

    :return: string sentence for showing year and period
    """
    result = Config.objects.first()
    return _("You are working in Year {}, {}").format(result.year, result.period)
