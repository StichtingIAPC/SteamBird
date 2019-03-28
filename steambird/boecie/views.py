from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView

from steambird.boecie.forms import CourseForm
from steambird.models import Study, Course, Teacher


class HomeView(View):
    def get(self, request):
        studies = Study.objects.all().order_by('study_type')

        context = {
            'studies': studies,
            # 'nav_items': ['foo']
        }
        return render(request, "boecie/index.html", context)


class StudyDetailView(DetailView):
    model = Study
    template_name = "boecie/study_detail.html"


class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "boecie/course_detail.html"

    # success_url = reverse_lazy("study.list")
    # TODO: make the success url a course_check_next function which returns a next course to check (within study)

    def get_context_data(self, **kwargs):
        context = super(CourseUpdateView, self).get_context_data()
        context['has_next'] = Course.objects.filter(study__id=self.kwargs['study'], updated_IAPC=False).exclude(
            course_code=self.kwargs['course_code']).first()
        return context

    def get_object(self, queryset=None):
        return Course.objects.get(course_code=self.kwargs['course_code'])

    def get_success_url(self):
        next_course = Course.objects.filter(study__id=self.kwargs['study'], updated_IAPC=False).first()
        if next_course is None:
            return reverse('study.list', kwargs={'pk': self.kwargs['study']})
        else:
            return reverse('course.detail',
                           kwargs={'study': self.kwargs['study'], 'course_code': next_course.course_code})


class TeachersListView(ListView):
    template_name = 'boecie/teachers_list.html'
    queryset = Teacher.objects.all()
    context_object_name = 'teachers'
    # paginate_by =
