from django.urls import path

from steambird.teacher.views import HomeView, ISBNLookupView, ISBNView, \
    CourseView, MSPDetail, AddMSPView, ISBNSearchApiView, DOISearchApiView, DOIDetailView, \
    ISBNDetailView

# pylint: disable=invalid-name
app_name = 'teacher'

# pylint: disable=invalid-name
urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('overview', CourseView.as_view(), name='courseview.list'),

    path('msp/<int:pk>', MSPDetail.as_view(), name='msp.detail'),
    path('msp/new', AddMSPView.as_view(), name='msp.new'),

    path('isbn/search/<str:isbn>', ISBNLookupView.as_view(), name='isbnlookup'),
    path('isbn', ISBNView.as_view(), name='isbn'),
    path('isbn/<str:isbn>', ISBNDetailView.as_view(), name='isbndetail'),
    path('doi/<str:doi>', DOIDetailView.as_view(), name='articledetail'),


    path('api/isbn/search', ISBNSearchApiView.as_view(), name='isbn.search'),
    path('api/doi/search', DOISearchApiView.as_view(), name='doi.search'),
]
