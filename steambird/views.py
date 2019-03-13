from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from steambird.models import Teacher, MaterialSelectionProcess as MSP
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from isbnlib.dev import NoDataForSelectorError

from .forms import ISBNForm
import isbnlib as i


class HomeView(View):
    def get(self, request):
        return render(request, "steambird/home.html")


class ISBNView(FormView):
    form_class = ISBNForm


    def get(self, request):

        form = ISBNForm()

        return render(request, 'steambird/ISBN.html', {'form': form})


    def form_valid(self, form):
        isbn = form.data['isbn']
        return redirect(reverse('isbndetail', kwargs={'isbn': isbn}))

    def form_invalid(self, form):
        return render(self.request, 'steambird/ISBN.html', {'form': form})


class ISBNDetailView(View):

    def get(self, request, isbn):


        try:
            meta_info = i.meta(isbn)
            # desc = i.desc(isbn)
            cover = i.cover(isbn)
            # print(meta_info, cover)
            try:
                meta_info['img'] = cover['thumbnail']
            except TypeError:
                meta_info['img'] = ['']
            # print(meta_info)

            return render(self.request, 'steambird/book.html', {'book': meta_info})
        except NoDataForSelectorError:
            return render(self.request, 'steambird/book.html', {'retrieved_data': "No data was found for given ISBN"})


class CourseView(View):

    def get(self, request):
        id = 1
        # courses = Course.objects.filter(Q(teachers=id)).prefetch_related()
        teacher = Teacher.objects.get(Q(id=id))
        # courses = teacher.course_set

        context = {
            'teacher': teacher
        }
        return render(request, "steambird/courseoverview.html", context)


class CourseViewDetail(View):

    def get(self, request, msp_key):
        msp_details = MSP.objects.get(id=msp_key)
        context = {
            'msp': msp_details
        }
        return render(request, "steambird/courseoverviewdetails.html", context)
