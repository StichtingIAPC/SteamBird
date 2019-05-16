import json

from django.http import HttpResponse
from isbnlib import *


def autocompleteISBNField(request):
    search_qr = request.REQUEST['search']
    result_info = info(search_qr)
    result_meta = meta(search_qr)
    print(result_info + '\n' + result_meta)

    response = request.REQUEST['callback'] + '(' + json.dumps(result_meta) + ");"
    return HttpResponse(response, content_type='aplication/json')
