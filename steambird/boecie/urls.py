from django.urls import path

from steambird.boecie.api_views import FindPeopleView
from steambird.boecie.views import CourseCreateView, CourseUpdateView, \
    HomeView, StudyDetailView, TeacherCreateView, TeacherDeleteView, \
    CourseStudyListView, CourseStudyDeleteView, TeacherEditView, TeachersListView, \
    LmlExport, ConfigView, CoursesListView, MSPDetail, MaterialListView

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
    path('study/<int:study>/courses', CoursesListView.as_view(), name='courses.overview'),

    path('teachers/', TeachersListView.as_view(), name='teacher.list'),
    path('teachers/new', TeacherCreateView.as_view(), name='teacher.create'),
    path('teachers/<int:pk>', TeacherEditView.as_view(), name='teacher.detail'),
    path('teachers/<int:pk>/delete', TeacherDeleteView.as_view(),
         name='teacher.delete'),
    path('msp/<int:pk>', MSPDetail.as_view(), name='msp.detail'),

    path('coursestudyrelations', CourseStudyListView.as_view(), name='coursestudy.list'),
    path('coursestudyrelations/<int:pk>/delete', CourseStudyDeleteView.as_view(),
         name='coursestudy.delete'),

    path('materials/overview', MaterialListView.as_view(), name='materials.list'),

    path('config/<int:pk>', ConfigView.as_view(), name='config'),
    # path('lml_export/', LmlExportOverView.as_view(), name='lmlexport.overview'),
    path('lml_export/', LmlExport.as_view(), name='lml_export'),

    path('api/find_teacher', FindPeopleView.as_view(), name='api_find_teacher'),
]

# pylint: disable=invalid-name
app_name = 'boecie'
