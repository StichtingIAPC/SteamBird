from django.db.models import Q
from django.shortcuts import render
from django.views import View
from steambird.models import Teacher, Course


class HomeView(View):
    def get(self, request):
        return render(request, "steambird/home.html")


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
