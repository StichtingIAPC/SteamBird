from json import dumps

from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.views.generic import FormView
from isbnlib.dev import NoDataForSelectorError


class IndexView(View):
    # pylint: disable=no-self-use
    def get(self, request):
        return render(request, "steambird/index.html")


