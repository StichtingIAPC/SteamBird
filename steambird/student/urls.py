from django.urls import path

from steambird.student.views import CoursesListView

# pylint: disable=invalid name
app_name = 'student'

# pylint: disable=invalid name
urlpatterns = [
    path('', CoursesListView.as_view(), name='index'),
]
