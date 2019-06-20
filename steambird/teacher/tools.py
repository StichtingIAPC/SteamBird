import isbnlib
from isbnlib.dev import NoDataForSelectorError

from crossref.restful import Works


# pylint: disable=invalid-name
works = Works()


def isbn_lookup(isbn):
    try:
        meta_info = isbnlib.meta(isbn)
        desc = isbnlib.desc(isbn)
        cover = isbnlib.cover(isbn)

        try:
            meta_info['img'] = cover['thumbnail']
        except (TypeError, KeyError):
            meta_info['img'] = None

        return {
            'meta': meta_info,
            'desc': desc,
            'cover': cover,
        }

    except NoDataForSelectorError:
        return None


def doi_lookup(doi):

    info = works.doi(doi)

    return info
