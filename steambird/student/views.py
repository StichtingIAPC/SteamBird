from collections import defaultdict

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView

from steambird.models import Course, Period
from steambird.student.forms import StudyCoursesFilterForm


class CoursesListView(FormView):
    """
    A view which shows all courses for a study. It is ordered just as Yx - Qy, looping over all
    quartiles in a year, for all years
    """
    form_class = StudyCoursesFilterForm
    template_name = "student/courses.html"
    success_url = reverse_lazy("student.index")

    def form_valid(self, form):
        data = form.cleaned_data

        result = {
            'periods': [],
            'study': data['study']
        }

        # Defines a base query configured to prefetch all resources that will
        #  be used either in this view or in the template.
        courses = Course.objects.with_self_and_parents().filter(
            studies__pk=data['study'].pk,
            calendar_year=data['calendar_year'],
            period=data['period']) \
            .order_by('coursestudy__study_year', 'period') \
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
        result['form'] = form

        return render(request=self.request,
                      template_name=self.template_name,
                      context=result)
