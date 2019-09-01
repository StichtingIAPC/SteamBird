from pkgutil import find_loader

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from pysidian_core.urls import urls as pysidian_core_urls

from steambird import settings
from steambird.views import IndexView, ISBNLookupView, ISBNView, ISBNDetailView, DOIDetailView, \
    ISBNSearchApiView, DOISearchApiView, AddMaterialView

from steambird.teacher.urls import urlpatterns as teacher_urls

# pylint: disable=invalid-name
urlpatterns = [
    path('select2/', include('django_select2.urls')),
    path('admin/', admin.site.urls),
    path('admin',
         RedirectView.as_view(pattern_name='admin:index', permanent=False)),
    path('teacher/', include(teacher_urls)),
    path('', IndexView.as_view(), name='index'),
    path('teacher/', include('steambird.teacher.urls', namespace='teacher')),
    path('boecie/', include('steambird.boecie.urls')),

    path('isbn/search/<str:isbn>', ISBNLookupView.as_view(), name='isbnlookup'),
    path('isbn', ISBNView.as_view(), name='isbn'),
    path('isbn/<str:isbn>', ISBNDetailView.as_view(), name='isbndetail'),
    path('doi/<str:doi>', DOIDetailView.as_view(), name='articledetail'),


    path('api/isbn/search', ISBNSearchApiView.as_view(), name='isbn.search'),
    path('api/doi/search', DOISearchApiView.as_view(), name='doi.search'),

    path('msp/new', AddMaterialView.as_view(), name='msp.new'),



] + pysidian_core_urls

if settings.DEBUG:
    import debug_toolbar

    # pylint: disable=invalid-name
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('translations/', include('rosetta.urls')),
    ] + urlpatterns

if find_loader('django_uwsgi'):
    # pylint: disable=invalid-name
    urlpatterns = [
        path('admin/uwsgi/', include('django_uwsgi.urls')),
    ] + urlpatterns
