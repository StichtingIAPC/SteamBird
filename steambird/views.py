
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from .forms import ISBNForm
import isbnlib as i


class HomeView(View):
    def get(self, request):
        return render(request, "steambird/home.html")


class ISBNView(View):
    def post(self, request):
        # create a form instance and populate it with data from the request:
        form = ISBNForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            isbn = form.data['isbn']
            meta_info = i.meta(isbn)
            # desc = i.desc(isbn)
            cover = i.cover(isbn)
            # print(meta_info, cover)
            meta_info['img'] = cover['thumbnail']
            # print(meta_info)

            return render(request, 'steambird/book.html', {'book': meta_info})
            # return HttpResponseRedirect('../')

        return render(request, 'steambird/ISBN.html', {'form': form})

        # if a GET (or any other method) we'll create a blank form

    def get(self, request):

        form = ISBNForm()

        return render(request, 'steambird/ISBN.html', {'form': form})
