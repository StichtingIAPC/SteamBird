from importlib import find_loader

from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView

from pysidian_core.urls import urls as pysidian_core_urls

from steambird import settings
from steambird.views import IndexView

urlpatterns = [
                  path('select2/', include('django_select2.urls')),
                  path('admin/', admin.site.urls),
                  path('admin', RedirectView.as_view(pattern_name='admin:index',
                                                     permanent=False)),
                  path('', IndexView.as_view(), name='index'),
                  path('teacher/', include('steambird.teacher.urls', namespace='teacher')),
                  path('boecie/', include('steambird.boecie.urls')),

              ] + pysidian_core_urls

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                      path('translations/', include('rosetta.urls'))
                  ] + urlpatterns

if find_loader('django_uwsgi'):
    urlpatterns = [
        path('admin/uwsgi/', include('django_uwsgi.urls'))
    ] + urlpatterns
