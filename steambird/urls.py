from pkgutil import find_loader

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from pysidian_core.urls import urls as pysidian_core_urls

from steambird import settings
from steambird.material_management.urls import urlpatterns as material_management_urls
from steambird.views import IndexView, TokenLogin

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
    path('token', TokenLogin.as_view(), name='token_login'),

] + pysidian_core_urls + material_management_urls

# https://docs.djangoproject.com/en/2.1/topics/http/views/#customizing-error-views
handler404 = 'steambird.views.handler404'
handler500 = 'steambird.views.handler500'
handler403 = 'steambird.views.permission_denied'
handler400 = 'steambird.views.bad_request'

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
