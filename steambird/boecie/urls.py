from django.urls import path

from steambird.boecie.views import HomeView, StudyDetailView, CourseUpdateView, TeachersListView, TeacherCreateView, \
    TeacherEditView, TeacherDeleteView, CourseCreateView

urlpatterns = [

    path('', HomeView.as_view(), name='index'),

    path('study/<int:pk>/', StudyDetailView.as_view(), name='study.list'),
    path('study/<int:pk>/create', CourseCreateView.as_view(), name='course.create'),
    path('study/<int:study>/course_detail/<int:course_code>/', CourseUpdateView.as_view(), name='course.detail'),

    path('teachers/', TeachersListView.as_view(), name='teacher.list'),
    path('teachers/new', TeacherCreateView.as_view(), name='teacher.create'),
    path('teachers/<int:pk>', TeacherEditView.as_view(), name='teacher.detail'),
    path('teachers/<int:pk>/delete', TeacherDeleteView.as_view(), name='teacher.delete')

    #     TODO: make courseview_detail work on CourseCode instead of pk
]
app_name = 'boecie'
