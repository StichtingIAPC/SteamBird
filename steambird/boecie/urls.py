from django.urls import path

from steambird.boecie.views import CourseCreateView, CourseUpdateView, \
    HomeView, StudyDetailView, TeacherCreateView, TeacherDeleteView, \
    TeacherEditView, TeachersListView, StudyCourseView, LmlExport

# pylint: disable=invalid-name
urlpatterns = [

    path('', HomeView.as_view(), name='index'),

    path('study/<int:pk>/', StudyDetailView.as_view(), name='study.list'),
    path('study/<int:pk>/create', CourseCreateView.as_view(),
         name='course.create'),
    # TODO: make courseview_detail work on CourseCode instead of pk
    #  so it is a human readable-ish url
    path('study/<int:study>/course_detail/<int:pk>/',
         CourseUpdateView.as_view(), name='course.detail'),

    path('teachers/', TeachersListView.as_view(), name='teacher.list'),
    path('teachers/new', TeacherCreateView.as_view(), name='teacher.create'),
    path('teachers/<int:pk>', TeacherEditView.as_view(), name='teacher.detail'),
    path('teachers/<int:pk>/delete', TeacherDeleteView.as_view(),
         name='teacher.delete'),

    path('test', StudyCourseView.as_view(), name='studycourse'),
    # path('lml_export/', LmlExportOverView.as_view(), name='lmlexport.overview'),
    path('lml_export/', LmlExport.as_view(), name='lmlexport.export'),
]

# pylint: disable=invalid-name
app_name = 'boecie'
