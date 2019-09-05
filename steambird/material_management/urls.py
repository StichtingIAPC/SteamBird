from django.urls import path

from .views import AddMaterialView, ISBNLookupView, ISBNView, ISBNDetailView, DOIDetailView, \
    ISBNSearchApiView, DOISearchApiView

# pylint: disable=invalid-name
urlpatterns = [
    path('isbn/search/<str:isbn>', ISBNLookupView.as_view(), name='isbnlookup'),
    path('isbn', ISBNView.as_view(), name='isbn'),
    path('isbn/<str:isbn>', ISBNDetailView.as_view(), name='isbndetail'),
    path('doi/<str:doi>', DOIDetailView.as_view(), name='articledetail'),


    path('api/isbn/search', ISBNSearchApiView.as_view(), name='isbn.search'),
    path('api/doi/search', DOISearchApiView.as_view(), name='doi.search'),

    path('msp/new', AddMaterialView.as_view(), name='msp.new'),

]
