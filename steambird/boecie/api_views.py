import re

from django import views
from django.http.response import HttpResponseBadRequest, JsonResponse
from vobject.base import Component

from steambird.util.import_from_ut_people import search_people, read_vcard


class FindPeopleView(views.View):
    @staticmethod
    def _get_first_name(name):
        search = re.search(r"\(([^\\]*)\)", name)

        return None if search is None else search.group(1)

    @staticmethod
    def _get_surname_prefix(full_name, family_name):
        search = re.search(r"\.([^.]*)$", full_name)

        return None if search is None else search.group(1)[1:-(len(family_name) + 3)]

    @staticmethod
    def _get_initials(given_name):
        search = re.search(r"^.*\.", given_name)

        return None if search is None else search.group(0)[1:]

    @staticmethod
    def _get_acedemic_title(full_name, initials):
        return full_name.split(initials)[0][:-1]

    @staticmethod
    def _serialize_vcard(vcard: Component):
        return {line.name: line.value for line in vcard.contents}

    # pylint: disable=no-self-use
    def get(self, request):
        if 'query' not in request.GET:
            return HttpResponseBadRequest()

        people = search_people(request.GET['query'])
        new_people = []

        for person in people:
            if person['type'] != 'person':
                continue

            vcard = read_vcard(person['vcard'])

            new_person = {
                **person,
                'first_name': FindPeopleView._get_first_name(person['name']),
            }

            if vcard is not None:
                initials = FindPeopleView._get_initials(vcard.n.value.given)
                new_person = {
                    **new_person,
                    'surname_prefix': FindPeopleView._get_surname_prefix(
                        str(vcard.n.value), vcard.n.value.family),
                    'family_name': vcard.n.value.family,
                    'initials': initials,
                    'acedemic_title': FindPeopleView._get_acedemic_title(vcard.fn.value, initials)
                }

            new_people.append(new_person)

        return JsonResponse(new_people, safe=False)
