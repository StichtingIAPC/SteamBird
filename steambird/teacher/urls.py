from django.urls import path

from steambird.teacher.views import HomeView, ISBNDetailView, ISBNView, \
    CourseView, MSPDetail, AddMSPView, ISBNSearchApiView

# pylint: disable=invalid-name
app_name = 'teacher'

# pylint: disable=invalid-name
urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('isbn/<str:isbn>', ISBNDetailView.as_view(), name='isbndetail'),
    path('isbn', ISBNView.as_view(), name='isbn'),
    path('overview', CourseView.as_view(), name='courseview.list'),
    path('msp/<int:pk>', MSPDetail.as_view(), name='msp.detail'),
    path('book/new', AddMSPVi   ew.as_view(), name='msp.new'),
    path('api/isbn/search', ISBNSearchApiView.as_view(), name='isbn.search'),
]