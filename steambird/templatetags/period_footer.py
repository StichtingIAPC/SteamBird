from django import template
from django.utils.translation import ugettext_lazy as _

from steambird.models.site_config import Config

# pylint: disable=invalid-name
register = template.Library()


@register.simple_tag()
def period_retrieval():
    result = Config.objects.first()
    return _("You are working in Year {}, {}").format(result.year, result.period)
