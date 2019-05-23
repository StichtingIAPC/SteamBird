import isbnlib
from isbnlib.dev import NoDataForSelectorError


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
