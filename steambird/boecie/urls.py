from django.urls import path, include

from steambird.boecie.views import HomeView, StudyDetailView, CourseUpdateView, TeachersListView


app_name = 'boecie'
urlpatterns = [

    path('', HomeView.as_view(), name='index'),
    path('study/<int:pk>/', StudyDetailView.as_view(), name='study.list'),
    path('study/<int:study>/course_detail/<int:course_code>/', CourseUpdateView.as_view(), name='course.detail'),
    path('teachers/', TeachersListView.as_view(), name='teachers_overview')
#     TODO: make courseview_detail work on CourseCode instead of pk
]