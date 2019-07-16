"""
Resolves UT-specific details to a useful URL
"""
from django import template

# pylint: disable=invalid-name
register = template.Library()


@register.simple_tag()
def osiris_url(course_code, calendar_year):
    """
    A template tag which resolves the params into a Osiris URL.
    Calendar Year is understood as Academic year which started in that year

    E.g. 2018 is understood as September 2018/ July 2019

    :param course_code: The course-code you are looking for. [0-9,a-z,A-Z] is possible
    :param calendar_year: int
    :return: Osiris URL for course_code in calendar_year
    """
    return "https://osiris.utwente.nl/student/OnderwijsCatalogusSelect.do" \
           "?selectie=cursus&cursus={}&collegejaar={}" \
        .format(course_code, calendar_year)


@register.simple_tag()
def people_utwente(initials, surname_prefix, surname):
    """
    Template tag which resolves teacher names into a people.utwente.nl URL

    :param initials: string
    :param surname_prefix: string
    :param surname: string
    :return: people.utwente.nl URL for given teacher
    """
    if surname_prefix is None:
        surname_prefix = ""

    return "https://people.utwente.nl/{}{}{}" \
        .format(initials, surname_prefix, surname).replace(' ', '')
