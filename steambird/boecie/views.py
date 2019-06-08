from collections import defaultdict

from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView, \
    DeleteView, FormView
from django_addanother.views import CreatePopupMixin

from steambird.boecie.forms import CourseForm, TeacherForm, StudyCourseForm
from steambird.models import Study, Course, Teacher, CourseStudy


class HomeView(View):
    # pylint: disable=no-self-use
    def get(self, request):
        context = {
            'types': defaultdict(list)
        }

        studies = Study.objects.all().order_by('type')

        for study in studies:
            course_total = study.course_set.count()
            courses_updated_teacher = study.course_set.filter(
                updated_teacher=True).count()
            courses_updated_associations = study.course_set.filter(
                updated_associations=True).count()
            context['types'][study.type].append({
                'name': study.name,
                'type': study.type,
                'id': study.pk,
                'courses_total': course_total,
                'courses_updated_teacher': courses_updated_teacher,
                'courses_updated_teacher_p':
                    (courses_updated_teacher / course_total * 100)
                    if course_total > 0 else 0,
                'courses_updated_association': courses_updated_associations,
                'courses_updated_association_p':
                    ((courses_updated_associations - courses_updated_teacher) /
                     course_total * 100) if course_total > 0 else 0
            })
        context["types"] = dict(context["types"])

        # TODO: Add fixed MSP (not yet finalized by teacher) count (?)
        return render(request, "boecie/index.html", context)


class StudyDetailView(FormView):
    model = Study
    form_class = StudyCourseForm(True)
    template_name = "boecie/study_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = Study.objects.get(pk=self.kwargs['pk'])
        return context


class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "boecie/course_form.html"

    # TODO: make the success url a course_check_next function which returns a
    #  next course to check (within study)

    def get_context_data(self, **kwargs):
        context = super(CourseUpdateView, self).get_context_data()
        context['is_edit'] = True
        context['has_next'] = Course.objects.filter(
            studies__id=self.kwargs['study'],
            updated_associations=False,
        ).exclude(
            course_code=self.kwargs['course_code'],
        ).first()

        return context

    def get_object(self, queryset=None):
        return Course.objects.get(course_code=self.kwargs['course_code'])

    def get_success_url(self):
        next_course = Course.objects.filter(studies__id=self.kwargs['study'],
                                            updated_associations=False).first()
        if next_course is None:
            return reverse('boecie:study.list',
                           kwargs={'pk': self.kwargs['study']})
        return reverse('boecie:course.detail',
                       kwargs={'study': self.kwargs['study'],
                               'course_code': next_course.course_code})


class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'boecie/course_form.html'

    def get_context_data(self, **kwargs):
        context = super(CourseCreateView, self).get_context_data()
        context['is_edit'] = False
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


class TeachersListView(ListView):
    template_name = 'boecie/teachers_list.html'
    queryset = Teacher.objects.all()
    context_object_name = 'teachers'


class TeacherEditView(UpdateView):
    template_name = 'boecie/teacher_form.html'
    model = Teacher
    form_class = TeacherForm
    success_url = reverse_lazy('boecie:teacher.list')


class TeacherCreateView(CreatePopupMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'boecie/teacher_form.html'

    def form_valid(self, form):
        teacher = form.save()
        teacher_pk = teacher.pk
        return redirect(
            reverse('boecie:teacher.detail', kwargs={'pk': teacher_pk}))


class TeacherDeleteView(DeleteView):
    model = Teacher
    success_url = reverse_lazy('boecie:teacher.list')
    template_name = 'boecie/teacher_confirm_delete.html'


class StudyCourseView(FormView):
    form_class = StudyCourseForm(True)
    template_name = 'boecie/studycourse_form.html'
