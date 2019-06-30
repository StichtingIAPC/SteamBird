import csv
import datetime
import io
from collections import defaultdict
from typing import Optional, Any

from django.forms import Form
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView, \
    DeleteView, FormView
from django_addanother.views import CreatePopupMixin

from steambird.boecie.forms import ConfigForm
from steambird.boecie.forms import CourseForm, TeacherForm, StudyCourseForm
from steambird.boecie.forms import LmlExportForm
from steambird.models import Book
from steambird.models import Config, MSP
from steambird.models import Study, Course, Teacher, CourseStudy
from steambird.models_coursetree import Period
from steambird.perm_utils import IsStudyAssociationMixin, IsBoecieMixin
from steambird.util import MultiFormView


class HomeView(IsBoecieMixin, View):
    # pylint: disable=no-self-use
    def get(self, request):
        context = {
            'types': defaultdict(list)
        }

        studies = Study.objects.all().order_by('type')
        year = Config.get_system_value('year')
        period = Config.get_system_value('period')

        for study in studies:
            course_total = study.course_set.filter(
                calendar_year=year,
                period=period).count()
            courses_updated_teacher = study.course_set.filter(
                updated_teacher=True,
                calendar_year=year,
                period=period).count()
            courses_updated_associations = study.course_set.filter(
                updated_associations=True,
                calendar_year=year,
                period=period).count()
            context['types'][study.type].append({
                'name': study.name,
                'type': study.type,
                'id': study.pk,
                'courses_total': course_total,
                'courses_updated_teacher': courses_updated_teacher,
                'courses_updated_teacher_p': round(
                    ((courses_updated_teacher / course_total * 100)
                     if course_total > 0 else 0), 2),
                'courses_updated_association': courses_updated_associations,
                'courses_updated_association_p':
                    round((((courses_updated_associations - courses_updated_teacher) /
                            course_total * 100) if course_total > 0 else 0), 2)
            })
        context["types"] = dict(context["types"])

        # TODO: Add fixed MSP (not yet finalized by teacher) count (?)
        return render(request, "boecie/index.html", context)


class StudyDetailView(IsStudyAssociationMixin, FormView):
    model = Study
    form_class = StudyCourseForm(True)
    template_name = "boecie/study_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = Study.objects.get(pk=self.kwargs['pk'])
        context['courses_not_updated'] = Course.objects.filter(
            calendar_year=Config.get_system_value("year"),
            period=Config.get_system_value("period"),
            studies=self.kwargs['pk'],
            updated_associations=False)
        context['courses_updated'] = Course.objects.filter(
            calendar_year=Config.get_system_value("year"),
            period=Config.get_system_value("period"),
            studies=self.kwargs['pk'],
            updated_associations=True)
        return context

    # For the small included form on the top of the page
    def form_valid(self, form):
        form.instance.study = Study.objects.get(pk=self.kwargs['pk'])
        form.save()
        return super(StudyDetailView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('boecie:study.list', kwargs={'pk': self.kwargs['pk']})


class CourseUpdateView(IsStudyAssociationMixin, MultiFormView):
    template_name = "boecie/course_form.html"
    forms = {
        'course_form': CourseForm,
        'studycourse_form': StudyCourseForm(has_course_field=False)
    }

    def get_object_for(self,
                       form_name: str,
                       request: HttpRequest) -> Optional[Any]:

        if form_name == 'course_form':
            return Course.objects.get(pk=self.kwargs['pk'])
        return super().get_object_for(form_name, request)

    # pylint: disable=arguments-differ
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['has_next'] = Course.objects.filter(
            studies__id=self.kwargs['study'],
            updated_associations=False,
        ).exclude(
            pk=self.kwargs['pk'],
        ).first()

        return context

    def form_valid(self, request: HttpRequest, form: Form, form_name: str) -> Optional[Any]:

        if form_name == 'course_form':
            form.instance.id = self.kwargs['pk']
            form.save()
            next_course = Course.objects.filter(studies__id=self.kwargs['study'],
                                                updated_associations=False).first()
            if next_course is None:
                return redirect(reverse('boecie:study.list',
                                        kwargs={'pk': self.kwargs['study']}))
            return redirect(reverse('boecie:course.detail',
                                    kwargs={'study': self.kwargs['study'],
                                            'pk': next_course.pk}))
        # elif form == 'studycourse_form'
        form.instance.course = Course.objects.get(pk=self.kwargs['pk'])
        form.save()
        return redirect(reverse('boecie:course.detail',
                                kwargs={'study': self.kwargs['study'],
                                        'pk': self.kwargs['pk']}))


class CourseCreateView(IsStudyAssociationMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'boecie/course_form.html'

    def get_context_data(self, **kwargs):
        context = super(CourseCreateView, self).get_context_data()
        context['is_edit'] = False
        context['course_form'] = context['form']
        return context

    def form_valid(self, form):
        if '_mark_updated' in self.request.POST:
            form.instance.updated_associations = True
        form.save(commit=True)

        study = Study.objects.get(pk=self.kwargs['pk'])
        course = Course.objects.get(course_code=form.cleaned_data['course_code'],
                                    period=form.cleaned_data['period'])
        CourseStudy.objects.create(study=study, course=course,
                                   study_year='1').save()  # TODO fix study_year

        return redirect(
            reverse('boecie:study.list', kwargs={'pk': self.kwargs['pk']}))


class TeachersListView(IsStudyAssociationMixin, ListView):
    template_name = 'boecie/teachers_list.html'
    queryset = Teacher.objects.all()
    context_object_name = 'teachers'


class TeacherEditView(IsStudyAssociationMixin, UpdateView):
    template_name = 'boecie/teacher_form.html'
    model = Teacher
    form_class = TeacherForm
    success_url = reverse_lazy('boecie:teacher.list')


class TeacherCreateView(IsStudyAssociationMixin, CreatePopupMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'boecie/teacher_form.html'

    def form_valid(self, form):
        teacher = form.save()
        teacher_pk = teacher.pk
        return redirect(
            reverse('boecie:teacher.detail', kwargs={'pk': teacher_pk}))


class TeacherDeleteView(IsStudyAssociationMixin, DeleteView):
    model = Teacher
    success_url = reverse_lazy('boecie:teacher.list')
    template_name = 'boecie/teacher_confirm_delete.html'


class StudyCourseView(IsStudyAssociationMixin, FormView):
    form_class = StudyCourseForm(has_course_field=True)
    template_name = 'boecie/studycourse_form.html'


class LmlExport(IsStudyAssociationMixin, FormView):
    template_name = 'boecie/lml_export_overview.html'

    form_class = LmlExportForm

    # pylint: disable = too-many-nested-blocks, too-many-branches
    def form_valid(self, form):
        form = form.cleaned_data

        period = Period[form.get('period')]

        result = io.StringIO()

        writer = csv.writer(result, delimiter=';', quotechar='"')
        writer.writerow('groep;vak;standaardvak;isbn;prognose;schoolBetaalt;verplicht;huurkoop;'
                        'vanprijs;korting;opmerking'.split(';'))

        if int(form.get('option')) < 4:
            for study in Study.objects.filter(type='bachelor'):
                courses = [c for c in Course.objects.filter(
                    coursestudy__study_year=int(form.get('option')),
                    calendar_year=form.get('year', Config.get_system_value('year')))
                           if c.falls_in(period)]

                for course in courses:
                    for msp in MSP.objects.filter(course=course):
                        if msp.resolved():
                            for book in msp.mspline_set.last().materials.all():
                                if isinstance(book, Book):
                                    writer.writerow(
                                        [
                                            study,
                                            'Module {year}.{period} - {name}'.format(
                                                year=form.get('option'),
                                                period=course.period[1],
                                                name=course.name
                                            ),
                                            '',
                                            book.ISBN,
                                            '',
                                            'n',
                                            'verplicht' if msp.mandatory else 'aanbevolen',
                                            'koop'
                                            '',
                                            '',
                                            ''
                                        ]
                                    )

        elif int(form.get('option')) == 4:
            for study in Study.objects.filter(type='master'):
                courses = [c for c in Course.objects.filter(
                    calendar_year=form.get('year', datetime.date.today().year)
                ) if c.falls_in(period)]

                for course in courses:
                    for msp in MSP.objects.filter(course=course):
                        if msp.resolved():
                            for book in msp.mspline_set.last().materials.all():
                                if isinstance(book, Book):
                                    writer.writerow(
                                        [
                                            study,
                                            '{name}'.format(
                                                name=course.name
                                            ),
                                            '',
                                            book.ISBN,
                                            '',
                                            'n',
                                            'verplicht' if msp.mandatory else 'aanbevolen',
                                            'koop'
                                            '',
                                            '',
                                            ''
                                        ]
                                    )
        elif int(form.get('option')) == 5:
            for study in Study.objects.filter('premaster'):
                courses = [c for c in Course.objects.filter(
                    calendar_year=form.get('year', datetime.date.today().year)
                ) if c.falls_in(period)]

                for course in courses:
                    for msp in MSP.objects.filter(course=course):
                        if msp.resolved():
                            for book in msp.mspline_set.last().materials.all():
                                if isinstance(book, Book):
                                    writer.writerow(
                                        [
                                            study,
                                            '{name}'.format(
                                                name=course.name
                                            ),
                                            '',
                                            book.ISBN,
                                            '',
                                            'n',
                                            'verplicht' if msp.mandatory else 'aanbevolen',
                                            'koop'
                                            '',
                                            '',
                                            ''
                                        ]
                                    )
        response = HttpResponse(result.getvalue(), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format('foobarbaz')
        return response


class ConfigView(UpdateView):
    template_name = 'boecie/config.html'
    model = Config
    form_class = ConfigForm

    def form_valid(self, form):
        form.instance.pk = 1
        form.save()
        return redirect(reverse_lazy('boecie:config', kwargs={'pk': 1}))
        # TODO: make this universal for more associations instead of just us, then pk will
        # match something with them
