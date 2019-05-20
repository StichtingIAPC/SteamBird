from django import template

# pylint: disable=invalid-name
register = template.Library()


@register.simple_tag()
def osiris_url(course_code, calendar_year):
    return "https://osiris.utwente.nl/student/OnderwijsCatalogusSelect.do" \
           "?selectie=cursus&cursus={}&collegejaar={}" \
        .format(course_code, calendar_year)


@register.simple_tag()
def people_utwente(initials, surname_prefix, surname):
    if surname_prefix is None:
        surname_prefix = ""
    return "https://people.utwente.nl/{}{}{}" \
        .format(initials, surname_prefix, surname).replace(' ', '')
