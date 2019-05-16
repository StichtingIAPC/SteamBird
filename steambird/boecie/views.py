from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django_addanother.views import CreatePopupMixin

from steambird.boecie.forms import CourseForm, TeacherForm
from steambird.models import Study, Course, Teacher, CourseStudy


class HomeView(View):
    def get(self, request):
        context = {
            'studies': []
        }

        studies = Study.objects.all().order_by('type')

        for study in studies:
            course_total = study.course_set.count()
            courses_updated_teacher = study.course_set.filter(updated_teacher=True).count()
            courses_updated_associations = study.course_set.filter(updated_associations=True).count()
            context['studies'].append({
                'name': study.name,
                'type': study.type,
                'id': study.pk,
                'courses_total': course_total,
                'courses_updated_teacher': courses_updated_teacher,
                'courses_updated_teacher_p': courses_updated_teacher / course_total * 100 if course_total > 0 else 0,
                # 'courses_msp_in_progress': study.course_set.filter(coursestudy__course__materials__resolved=False),
                # 'courses_updated_associations': study.course_set.filter(
                #     Q(updated_associations=True) & Q(updated_teacher=False) & ~Q(
                #         coursestudy__course__materials__resolved=False)).count(),
                'courses_updated_association': courses_updated_associations,
                'courses_updated_association_p': (courses_updated_associations-courses_updated_teacher) / course_total * 100 if course_total > 0 else 0
            })

        return render(request, "boecie/index.html", context)


class StudyDetailView(DetailView):
    model = Study
    template_name = "boecie/study_detail.html"


class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "boecie/course_form.html"

    # success_url = reverse_lazy("study.list")
    # TODO: make the success url a course_check_next function which returns a next course to check (within study)

    def get_context_data(self, **kwargs):
        context = super(CourseUpdateView, self).get_context_data()
        context['is_edit'] = True
        context['has_next'] = Course.objects.filter(studies__id=self.kwargs['study'],
                                                    updated_associations=False).exclude(
            course_code=self.kwargs['course_code']).first()
        return context

    def get_object(self, queryset=None):
        return Course.objects.get(course_code=self.kwargs['course_code'])

    def get_success_url(self):
        next_course = Course.objects.filter(studies__id=self.kwargs['study'], updated_associations=False).first()
        if next_course is None:
            return reverse('boecie:study.list', kwargs={'pk': self.kwargs['study']})
        else:
            return reverse('boecie:course.detail',
                           kwargs={'study': self.kwargs['study'], 'course_code': next_course.course_code})


class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'boecie/course_form.html'

    def get_context_data(self, **kwargs):
        context = super(CourseCreateView, self).get_context_data()
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        course = form.save(commit=False)
        if '_mark_updated' in self.request.POST:
            course.updated_associations = True  # TODO make this work
        course.save()
        study = Study.objects.get(pk=self.kwargs['pk'])

        CourseStudy.objects.create(study=study, course=course, study_year='1').save()  # TODO fix study_year
        return redirect(reverse('boecie:study.list', kwargs={'pk': self.kwargs['pk']}))

        # automatically add to study, if study pk exists


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
        return redirect(reverse('boecie:teacher.detail', kwargs={'pk': teacher_pk}))

    def form_invalid(self, form):
        return render(self.request, 'boecie:teacher.create')


class TeacherDeleteView(DeleteView):
    model = Teacher
    success_url = reverse_lazy('boecie:teacher.list')
    template_name = 'boecie/teacher_confirm_delete.html'
