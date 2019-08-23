import csv
import datetime
import io
import logging
from collections import defaultdict
from typing import Optional, Any

from django.db.models import Count, Q
from django.forms import Form
from django.http import HttpRequest, Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView, \
    DeleteView, FormView, TemplateView
from django_addanother.views import CreatePopupMixin

from steambird.boecie.forms import CourseForm, TeacherForm, StudyCourseForm, \
    ConfigForm, LmlExportForm
from steambird.models import Config, MSP, MSPLineType, MSPLine, Book
from steambird.models import Study, Course, Teacher, CourseStudy
from steambird.models_coursetree import Period
from steambird.perm_utils import IsStudyAssociationMixin, IsBoecieMixin
from steambird.teacher.forms import PrefilledSuggestAnotherMSPLineForm, \
    PrefilledMSPLineForm
from steambird.util import MultiFormView


logger = logging.getLogger(__name__)


class HomeView(IsBoecieMixin, View):
    # pylint: disable=no-self-use
    def get(self, request):
        context = {
            'types': defaultdict(list)
        }

        year = Config.get_system_value('year')
        period = Config.get_system_value('period')

        studies = Study.objects.order_by('type') \
            .annotate(course_total=Count('course', filter=Q(
                course__period=period,
                course__calendar_year=year))) \
            .annotate(courses_updated_teacher=Count('course', filter=Q(
                course__updated_teacher=True,
                course__period=period,
                course__calendar_year=year))) \
            .annotate(courses_updated_assications=Count('course', filter=Q(
                course__updated_associations=True,
                course__period=period,
                course__calendar_year=year)))

        for study in studies:
            course_total = study.course_total
            courses_updated_teacher = study.courses_updated_teacher
            courses_updated_associations = study.courses_updated_assications
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


class CoursesListView(IsStudyAssociationMixin, TemplateView):
    template_name = "boecie/courses.html"

    # pylint: disable=arguments-differ
    def get_context_data(self, study):
        year = Config.get_system_value('year')

        result = {
            'periods': [],
            'study': Study.objects.get(pk=study)
        }

        # Defines a base query configured to prefetch all resources that will
        #  be used either in this view or in the template.
        courses = Course.objects.with_all_periods().filter(
            studies__pk=study,
            calendar_year=year)\
            .order_by('coursestudy__study_year', 'period')\
            .prefetch_related('coursestudy_set', 'coordinator')

        per_year_quartile = defaultdict(list)

        # The first execution of this line executes the entire `course`
        #  query. After this ,the result of that query is cached.
        for course in courses:
            # As coursestudy_set was prefetched, this will not execute a second
            #  query.
            for coursestudy in course.coursestudy_set.all():
                for period in course.period_all:
                    period_obj = Period[period]
                    if period_obj.is_quartile():
                        per_year_quartile[(coursestudy.study_year, period_obj)].append(course)

        result['periods'] = list(map(
            lambda x: {
                'quartile': x[0][1],
                'year': x[0][0],
                'courses': x[1]
            },
            sorted(per_year_quartile.items(), key=lambda x: (x[0][0], x[0][1]))
        ))

        return result


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

    # pylint: disable=arguments-differ
    def get_context_data(self):
        result = super(TeacherEditView, self).get_context_data()
        result['courses'] = Teacher.objects.get(pk=self.kwargs['pk']).all_courses_period(
            year=Config.get_system_value('year'),
            period=Config.get_system_value('period')
        )
        return result


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
                courses = [c for c in Course.objects.with_all_periods().filter(
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


class MSPDetail(IsStudyAssociationMixin, FormView):
    """
    This is quite a complex view. It extends a form view, as its primary action
    is the creation of MSP lines. Even though this view uses multiple forms,
    only one type of form can be saved. This is fine, since all forms in this
    view concern the same data-structure.
    """

    template_name = "boecie/msp/detail.html"
    form_class = PrefilledSuggestAnotherMSPLineForm

    def get_success_url(self):
        """
        Makes sure that the view returns to the MSP overview after submission
        of a form.

        :return: the URL that points to the current view.
        """
        return reverse('boecie:msp.detail', kwargs={
            'pk': self.kwargs.get("pk"),
        })

    def form_valid(self, form):
        """
        Makes sure the data is saved after submission.

        :param form: The form and its data.
        :return: a redirect to get_success_url.
        """
        form.save(commit=True)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            "Invalid MSPLine create body submitted, with errors: {}",
            form.errors,
        )

        if form.is_valid():
            logger.critical("Valid form handled by form_invalid?", form)
        return super().form_invalid(form)

    def get_initial(self):
        """
        Fills in initial data for the primary form. The primary form is the
        form at the bottom of the page, where the teacher can request other
        study materials if need be.

        :return: Initial form data
        """
        initial = super().get_initial()
        initial["msp"] = self.kwargs.get("pk")
        initial["type"] = MSPLineType.request_material.name

        return initial

    def get_context_data(self, **kwargs):
        """
        Constructs the context (apart from the primary form). This means that it
        will generate all secondary forms, and meta data for allowing proper
        and nice-looking renderings of the view.

        :param kwargs: ¯\\_(ツ)_/¯
        :return: a context
        """
        try:
            msp = MSP.objects.get(pk=self.kwargs.get("pk"))
        except MSPLine.DoesNotExist:
            raise Http404

        data = super().get_context_data(**kwargs)
        # The main MSP
        data["msp"] = msp
        # List of MSPLines with metadata
        data["lines"] = []
        # Tracks whether the last line is a approve_material line.
        data["finished"] = False

        # Tracks the line that is the last "set_available_materials" line.
        last_available = {"last_available": False}
        for line in msp.mspline_set.all():
            data["lines"].append({
                "line": line,
                "materials": [],
            })

            if line.type == MSPLineType.set_available_materials.name:
                # Swaps the last_available MSPLine of type available_materials
                # to the current line.
                last_available["last_available"] = False
                last_available = data["lines"][-1]
                last_available["last_available"] = True

            for material in line.materials.all():
                data["lines"][-1]["materials"].append({
                    "material": material
                })

                if line.type == 'set_available_materials':
                    data["lines"][-1]["materials"][-1]["form"] = \
                        PrefilledMSPLineForm({
                            "msp": msp.pk,
                            "comment": "",
                            "materials": [material.pk],
                            "type": "approve_material",
                        })

                # Tracks whether this MSP is finished.
                if line.type == MSPLineType.approve_material.name:
                    data["finished"] = True
                else:
                    data["finished"] = False
        data["set_avail_form"] = PrefilledSuggestAnotherMSPLineForm({
            'msp': self.kwargs.get("pk"),
            'type': MSPLineType.set_available_materials.name,
        })

        return data
