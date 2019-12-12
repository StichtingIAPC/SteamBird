"""
This module contains all the Views which setup the data used in the Boecie admin-side templates.
"""

import csv
import datetime
import io
import logging
from collections import defaultdict
from typing import Optional, Any, Dict, Type

from django.contrib.auth.models import User
from django.db.models import Count, Q, QuerySet
from django.forms import Form, ModelForm
from django.http import HttpRequest, Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView, \
    DeleteView, FormView, TemplateView
from django_addanother.views import CreatePopupMixin

from steambird.boecie.forms import ConfigForm, get_course_form, TeacherForm, \
    StudyCourseForm, LmlExportForm, MSPCreateForm
from steambird.models import Book, Config, MSP, Study, Course, Teacher, \
    CourseStudy, MSPLineType, MSPLine, StudyMaterialEdition, AuthToken
from steambird.models.coursetree import Period
from steambird.perm_utils import IsStudyAssociationMixin, IsBoecieMixin
from steambird.teacher.forms import PrefilledSuggestAnotherMSPLineForm, \
    PrefilledMSPLineForm
from steambird.util import MultiFormView


LOGGER = logging.getLogger(__name__)


class HomeView(IsStudyAssociationMixin, View):
    """
    View that creates the Home-page of the Boecie view. Shows which courses you are linked to as
    user (through association reference). Also shows progress bars to show how far a study is
    coming along, even in the updating done by the association.
    """
    # pylint: disable=no-self-use
    def get(self, request: HttpRequest):
        """
        Function in which we set up the context for use in the actual rendering of the page.
        Get is used to retrieve data related to the studies for the graphing.

        :param request: Django HttpRequest object
        :return: template renderer with args: request, template location, context, \
        django eventually turns this into a HttpResponse (see signature).
        """

        # TODO: limit to study association you are part of
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
    """
    View which shows details about a certain Study. You can add courses from this page, and you
    have an overview of how much still needs to be updated. It also offers the user the option to
    add a new study directly from the page. Uses features from form-view to achieve all this,
    including overwriting some base-settings such as context-data.
    """

    model = Study
    form_class = StudyCourseForm(True)
    template_name = "boecie/study_detail.html"

    def get_context_data(self, **kwargs: Dict[str, Any]):
        """
        Defines what we expect as context-data. Retrieves course objects based on the study in two
        sets: updated and to-be-updated courses. Retrieved sets are limited to the current period.

        :param kwargs: keyword arguments, retrieved from the URL, also see url_listing
        :return: Dictionary containing the context
        """

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
    def form_valid(self, form: Form) -> HttpResponseRedirect:
        """
        If the form is valid, save to the associated model. Sets the hidden-field
        to a valid id before saving.

        :param form: form object
        :return: HttpResponRedirect defined by get_success_url
        """

        form.instance.study = Study.objects.get(pk=self.kwargs['pk'])
        form.save()
        return super(StudyDetailView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('boecie:study.list', kwargs={'pk': self.kwargs['pk']})


class CoursesListView(IsStudyAssociationMixin, TemplateView):
    """
    A view which shows all courses for a study. It is ordered just as Yx - Qy, looping over all
    quartiles in a year, for all years
    """

    template_name = "boecie/courses.html"

    # pylint: disable=arguments-differ
    def get_context_data(self, study: int):
        """
        A function which returns the context structured on all courses per period, for every year

        :param study: The database PK which is used to resolve the study
        :return: Context
        """

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
    """
    The view which provides the filled in form of the CourseForm, to act as an EditView. It makes
    use of the MultiFormView to also be able to show the StudyCourseForm as well as the CourseForm.

    The MultiFormView is an internally written View, for questions regarding that,
    ask @rkleef
    """

    template_name = "boecie/course_form.html"

    def get_forms_classes(self) -> Dict[str, Type[Form]]:
        return {
            'studycourse_form': StudyCourseForm(has_course_field=False),
            'course_form': get_course_form(course_id=self.kwargs['pk'])
        }

    def get_object_for(self,
                       form_name: str,
                       request: HttpRequest) -> Optional[Any]:
        """
        Gets the Course object for CourseForm if form_name = course_form, or returns the super
        if other.

        :param form_name: the name of the form (can either be CourseForm or StudyCourseForm here)
        :param request: Django HttpRequest object
        :return: Course object or nothing (if studycourse_form)
        """

        if form_name == 'course_form':
            return Course.objects.get(pk=self.kwargs['pk'])
        return super().get_object_for(form_name, request)

    # pylint: disable=arguments-differ
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extends context data with a few things used for the course_form template
        (which is shared with the CreateView). Has two extra bools for 'intelligent' UI-flow

        Context description:
            context['is_edit'] -> Bool which returns True if Edit view

            context['has_next'} -> Query based bool, is true if there is another not yet updated \
            course

        :param kwargs: kwargs as defined by URL Listing
        :return: context data dict
        """

        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['has_next'] = Course.objects.filter(
            studies__id=self.kwargs['study'],
            updated_associations=False,
        ).exclude(
            pk=self.kwargs['pk'],
        ).first()

        return context

    def form_valid(self, request: HttpRequest, form: Form, form_name: str) -> HttpResponseRedirect:
        """
        Method which checks if the form is valid. Has a bit more complexity than most form_valid
        due to the M2M fields like teachers and MSP's. We also need to check which form has been
        submitted. Save's valid forms content and fills in any leftover hidden fields

        :param request: Django HtppRequest object
        :param form: Django Form object
        :param form_name: form name, see forms dict of the class
        :return: HttpResponseRedirect object
        """

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
    """
    Class for the creation of Courses, this view automatically ties the course to the study it
    was called from
    """

    model = Course
    form_class = get_course_form()
    template_name = 'boecie/course_form.html'

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gets a bit extra context data because form-template is shared with update view. Extra parts:
            context['is_edit'] -> Bool, always False in this view

            context['course_form'] -> Rename of form, prevents confusion

        :param kwargs: Kwargs as given by URL, see URL Listing
        :return: context dictionary
        """

        context = super(CourseCreateView, self).get_context_data()
        context['is_edit'] = False
        context['course_form'] = context['form']
        return context

    def form_valid(self, form: Form) -> HttpResponseRedirect:
        """
        Handles logic of when form is valid. Handles the two submit buttons actions, also handles
        creating course-stuyd relation

        :param form: Django Form object
        :return: Django HttpResonseRedirect
        """

        if '_mark_updated' in self.request.POST:
            form.instance.updated_associations = True
        form.save(commit=True)


        study = Study.objects.get(pk=self.kwargs['pk'])
        course = Course.objects.get(course_code=form.cleaned_data['course_code'],
                                    period=form.cleaned_data['period'])
        CourseStudy.objects.create(study=study, course=course,
                                   study_year=int(form.cleaned_data['study_year'])).save()  # TODO fix study_year

        return redirect(
            reverse('boecie:study.list', kwargs={'pk': self.kwargs['pk']}))


class TeachersListView(IsStudyAssociationMixin, ListView):
    """
    A view which shows all teachers that we have within the system, in a list form.
    Fairly straightforward usage of Django ListView
    """

    template_name = 'boecie/teachers_list.html'
    queryset = Teacher.objects.all()
    context_object_name = 'teachers'


class TeacherEditView(IsStudyAssociationMixin, UpdateView):
    """
    An update view in which users can edit/update the information we have on teachers.
    Also shows the last Login of said teacher. Uses same template as TeacherCreateView
    """

    template_name = 'boecie/teacher_form.html'
    model = Teacher
    form_class = TeacherForm
    success_url = reverse_lazy('boecie:teacher.list')

    # pylint: disable=arguments-differ
    def get_context_data(self) -> Dict[str, Any]:
        """
        Retrieves the data of which courses a teacher gives over the entire year and puts it into
        the context variable.

        :return: Dictionary object
        """

        result = super(TeacherEditView, self).get_context_data()
        result['courses'] = Teacher.objects.get(pk=self.kwargs['pk']).all_courses_year(
            year=Config.get_system_value('year')
        )
        return result


class TeacherCreateView(IsStudyAssociationMixin, CreatePopupMixin, CreateView):
    """
    A view used for the creation of new Teachers. Is also used as a pop-up the CourseForm pages,
    hence it uses the CreatePopupMixin. Uses the same template as TeacherEditView
    """

    model = Teacher
    form_class = TeacherForm
    template_name = 'boecie/teacher_form.html'

    def form_valid(self, form: Form) -> HttpResponseRedirect:
        """
        Checks if the Form is valid. Redirects to the 'edit' page of the same teacher

        :param form: Django Form object
        :return: Django HttpResponseRedirect
        """

        teacherinfo = form.save(commit=False)
        lastname = str()
        if teacherinfo.surname_prefix is not None:
            lastname += teacherinfo.surname_prefix
        lastname += teacherinfo.last_name

        # Create a Django User object, so we can then create a Authcode and Teacher object to
        # link it to.
        user = User()
        user.first_name = teacherinfo.first_name
        user.last_name = lastname
        user.username = teacherinfo.initials.replace('.', '') + teacherinfo.last_name
        user.password = 'AC0mpl3t3lyRandomPasSwORDThatSh08dNevahbeUsed'
        user.set_unusable_password()
        user.save()

        # Create an AuthToken that can be used for the Teacher
        authcode = AuthToken()
        authcode.user = user
        authcode.save()

        # Create
        teacher = form.save(commit=False)
        teacher.user = user

        teacher.save()
        teacher_pk = teacher.pk
        return redirect(
            reverse('boecie:teacher.detail', kwargs={'pk': teacher_pk}))


class TeacherDeleteView(IsStudyAssociationMixin, DeleteView):
    """
    Simple delete-view. Checks if you are really sure if you want to delete this person
    (making sure accidental clicks don't ruin your system)
    """

    model = Teacher
    success_url = reverse_lazy('boecie:teacher.list')
    template_name = 'boecie/teacher_confirm_delete.html'


class CourseStudyListView(IsStudyAssociationMixin, ListView):
    """
    A view which shows all Course-study relations that are found in the database. Only selects the
    relations for the current set year in Config.
    """

    template_name = 'boecie/coursestudy.html'
    model = CourseStudy
    context_object_name = 'coursestudy_relation'

    def get_queryset(self) -> QuerySet:
        """
        Gets the queryset with course-study relations, ordered on study name, for current year

        :return: Django Queryset object
        """

        config = Config.objects.first()
        result = CourseStudy.objects.filter(
            course__calendar_year=config.year).order_by('study__name')\
            .prefetch_related('course', 'study')
        return result


class CourseStudyDeleteView(IsBoecieMixin, DeleteView):
    """
    A view in which we make sure that you want to delete a Course-Study relation.
    Should only be accessible by Association-super-user
    """

    template_name = 'boecie/coursestudy_confirm_delete.html'
    model = CourseStudy
    context_object_name = 'coursestudy_relation'
    success_url = reverse_lazy('boecie:coursestudy.list')


class LmlExport(IsStudyAssociationMixin, FormView):
    """
    A view in which a user can select their export options. For options see :any:`LmlExportOptions`
    """

    template_name = 'boecie/lml_export_overview.html'
    form_class = LmlExportForm

    # pylint: disable = too-many-nested-blocks, too-many-branches
    def form_valid(self, form: Form) -> HttpResponse:
        """
        Validates if the form submitted contains valid options, returns a download for
        those options.

        :param form: Django Form object
        :return: Django HttpResponse object
        """

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


class ConfigView(IsBoecieMixin, UpdateView):
    """
    This view is to edit the site-wide config.
    """

    template_name = 'boecie/config.html'
    model = Config
    form_class = ConfigForm

    def form_valid(self, form: Form) -> HttpResponseRedirect:
        """
        If the form is valid, this will be triggered.

        :param form: The submitted form
        :return: Django HttpResponseRedirect
        """

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
        new_mspline = form.save(commit=False)
        new_mspline.created_by = self.request.user
        new_mspline.created_by_side = "BOECIE"
        new_mspline.save()
        form.save_m2m()
        return super().form_valid(form)

    def form_invalid(self, form):
        LOGGER.warning(
            "Invalid MSPLine create body submitted, with errors: {}",
            form.errors,
        )

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


class MaterialListView(IsStudyAssociationMixin, TemplateView):
    """
    A view which gives us a list of all materials which are currently in the
    system. List should be ordered based on type. Future improvements should
    focus on better filters
    """

    template_name = 'boecie/materials_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        materials = StudyMaterialEdition.objects \
            .select_related('polymorphic_ctype')\
            .order_by('polymorphic_ctype')\
            .all()

        grouped = defaultdict(list)

        for material in materials:
            grouped[str(material.polymorphic_ctype)].append(material)

        context['grouped_materials'] = dict(grouped)

        return context


class MSPCreateView(IsStudyAssociationMixin, CreateView):
    template_name = 'boecie/material_add.html'
    model = MSP
    form_class = MSPCreateForm

    def get_success_url(self):
        return reverse('boecie:msp.detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form: ModelForm):
        line: MSPLine = form.save(commit=False)
        line.created_by = self.request.user
        line.created_by_side = "BOECIE"
        line.type = MSPLineType.request_material.name
        line.msp = MSP.objects.create()
        line.msp.course_set.set([self.kwargs['course']])
        line.save()

        # noinspection PyAttributeOutsideInit
        # pylint: disable=attribute-defined-outside-init
        self.object = line.msp

        form.save_m2m()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        LOGGER.info("Invalid input received by the MSP create view.")

        return super().form_invalid(form)
