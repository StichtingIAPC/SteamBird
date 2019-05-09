from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from steambird.models import Teacher, MSP
from django.views.generic import FormView, DetailView
from isbnlib.dev import NoDataForSelectorError

from steambird.perm_utils import IsTeacherMixin
from .forms import ISBNForm
import isbnlib as i


class HomeView(IsTeacherMixin, View):

    def get(self, request):
        return render(request, "steambird/teacher/home.html")


class ISBNView(IsTeacherMixin, FormView):
    form_class = ISBNForm
    template_name = 'steambird/teacher/ISBN.html'


    def form_valid(self, form):
        isbn = form.data['isbn']
        return redirect(reverse('teacher:isbndetail', kwargs={'isbn': isbn}))

    def form_invalid(self, form):
        return render(self.request, 'steambird/teacher/ISBN.html', {'form': form})


class ISBNDetailView(IsTeacherMixin, View):

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

            return render(self.request, 'steambird/teacher/book.html', {'book': meta_info})
        except NoDataForSelectorError:
            return render(self.request, 'steambird/teacher/book.html', {'retrieved_data': "No data was found for given ISBN"})


class CourseView(IsTeacherMixin, DetailView):

    template_name = 'steambird/teacher/courseoverview.html'

    def get_queryset(self):
        return Teacher.objects.get(user=self.request.user)



class CourseViewDetail(IsTeacherMixin, DetailView):

    template_name = 'steambird/teacher/courseoverviewdetails.html'

    def get_queryset(self):
        return MSP.objects.filter(Q(course__teachers__user=self.request.user) |
                           Q(course__coordinator__user=self.request.user), pk=self.request.pk)
