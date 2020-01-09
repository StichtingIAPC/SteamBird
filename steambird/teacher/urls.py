from django.urls import path

from steambird.teacher.views import HomeView, CourseView, MSPDetail, CourseDeleteMSPView

# pylint: disable=invalid-name
app_name = 'teacher'

# pylint: disable=invalid-name

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('overview', CourseView.as_view(), name='courseview.list'),
    path('overview/<int:pk>/delete', CourseDeleteMSPView.as_view(),
         name='courseviewMSP.delete'),

    path('msp/<int:pk>', MSPDetail.as_view(), name='msp.detail'),



]
