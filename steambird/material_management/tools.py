from typing import Optional

import isbnlib
from isbnlib import NotValidISBNError
from isbnlib.dev import NoDataForSelectorError

from crossref.restful import Works


# pylint: disable=invalid-name
works = Works()


def isbn_lookup(isbn: str):
    """
    Tool that uses isbnlib to look up information for the given ISBN.

    :param isbn: ISBN in string format, as ISBN can also have some letters and dashes
    :return: Dict with data, or None
    """
    try:
        meta_info = isbnlib.meta(isbn)
        if meta_info is None:
            raise NotValidISBNError(isbn)
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


def doi_lookup(doi: str) -> Optional[dict]:
    """
    Tool that uses crossref package to retrieve information based on DOI inputted

    :param doi: DOI of any kind
    :return: Dictionary containing (a lot of) info or None
    """

    info = works.doi(doi)

    return info
