from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from pysidian_core.urls import urls as pysidian_core_urls

from steambird import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin', RedirectView.as_view(pattern_name='admin:index',
                                       permanent=False)),
    path('teacher/', include('steambird.teacher.urls', namespace='teacher')),
              ] + pysidian_core_urls

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                      path('translations/', include('rosetta.urls'))
                  ] + urlpatterns
