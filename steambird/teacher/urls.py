from django.urls import path

from steambird.teacher.views import HomeView, ISBNDetailView, ISBNView, CourseView, CourseViewDetail

app_name = 'teacher'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('isbn/<str:isbn>', ISBNDetailView.as_view(), name='isbndetail'),
    path('isbn', ISBNView.as_view(), name='isbn'),
    path('overview', CourseView.as_view(), name='courseview.list'),
    path('overview/<int:msp_key>', CourseViewDetail.as_view(), name='courseview.details')]
