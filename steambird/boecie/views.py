from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView

from steambird.models import Study


class HomeView(View):
    def get(self, request):
        studies = Study.objects.all().order_by('study_type')

        context = {
            'studies': studies
        }
        return render(request, "boecie/index.html", context)


class StudyDetailView(DetailView):
    model = Study
    template_name = "boecie/study_detail.html"




# {% for course in study.courses.all %}#}
# {{ course.name }}#}
# {% endfor %}#}
