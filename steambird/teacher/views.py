from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views import View

import isbnlib
from json import dumps


class AddMSPView(View):
    def get(self, request):
        return render(self.request, 'steambird/new_book.html')

    def post(self, request):
        pass


class ISBNSearchApiView(View):
    def post(self, request):
        try:
            meta_info = isbnlib.meta(request.GET['isbn'])
            cover = isbnlib.cover(request.GET['isbn'])

            return JsonResponse({**meta_info, **cover})
        except isbnlib.ISBNLibException as e:
            return HttpResponseBadRequest(dumps(str(e)),
                                          content_type="application/json")
