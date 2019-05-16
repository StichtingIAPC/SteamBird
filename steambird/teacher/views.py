import isbnlib as i
from django.db.models import Q
from django.forms import HiddenInput, ChoiceField
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, CreateView, TemplateView
from django_select2.forms import Select2Widget
from isbnlib.dev import NoDataForSelectorError

from steambird.models import Teacher, MSP
from steambird.models_msp import MSPLine, MSPLineType
from .forms import ISBNForm, PrefilledMSPLineForm, \
    PrefilledSuggestAnotherMSPLineForm


class HomeView(View):
    def get(self, request):
        return render(request, "steambird/teacher/home.html")


class ISBNView(FormView):
    form_class = ISBNForm
    template_name = 'steambird/teacher/ISBN.html'

    def form_valid(self, form):
        isbn = form.data['isbn']
        return redirect(reverse('teacher:isbndetail', kwargs={'isbn': isbn}))

    def form_invalid(self, form):
        return render(self.request, 'steambird/teacher/ISBN.html', {'form': form})


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

            return render(self.request, 'steambird/teacher/book.html', {'book': meta_info})
        except NoDataForSelectorError:
            return render(self.request, 'steambird/teacher/book.html', {'retrieved_data': "No data was found for given ISBN"})


class CourseView(View):

    def get(self, request):
        id = 1
        # courses = Course.objects.filter(Q(teachers=id)).prefetch_related()
        teacher = Teacher.objects.get(Q(id=id))
        # courses = teacher.course_set

        context = {
            'teacher': teacher
        }
        return render(request, "steambird/teacher/courseoverview.html", context)


class CourseViewDetail(View):

    def get(self, request, msp_key):
        msp_details = MSP.objects.get(id=msp_key)
        context = {
            'msp': msp_details
        }
        return render(request, "steambird/teacher/courseoverviewdetails.html", context)


class MSPTestView(TemplateView):
    template_name = "steambird/teacher/msp/detail.html"

    def get_context_data(self, **kwargs):
        try:
            msp = MSP.objects.get(pk=self.kwargs.get("pk"))
        except MSPLine.DoesNotExist:
            raise Http404

        data = super().get_context_data(**kwargs)

        data["lines"] = []
        for line in msp.mspline_set.all():
            data["lines"].append({
                "line": line,
                "materials": [],
            })
            for material in line.materials.all():
                data["lines"][-1]["materials"].append({
                    "material": material
                })

                if line.type == 'set_available_materials':
                    data["lines"][-1]["materials"][-1]["form"] =\
                        PrefilledMSPLineForm({
                            "msp": msp.pk,
                            "comment": "",
                            "materials": [material.pk],
                            "type": "approve_material",
                        })
        data["suggest_another"] = PrefilledSuggestAnotherMSPLineForm({
            "msp": msp.pk,
            "type": "request_material"
        })

        return data
