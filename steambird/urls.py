from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView

from pysidian_core.urls import urls as pysidian_core_urls

from steambird import settings
from steambird.views import HomeView, ISBNView, ISBNDetailView, CourseView, CourseViewDetail

urlpatterns = [
                  path('select2/', include('django_select2.urls')),

                  # Administration pages (beheer app)
                  # path('boecie/', RedirectView.as_view(url=reverse_lazy('admin_index'))),
                  path('boecie/', include('steambird.boecie.urls')),

                  path('', HomeView.as_view(), name='index'),
                  path('admin/', admin.site.urls),
                  path('admin', RedirectView.as_view(pattern_name='admin:index',
                                                     permanent=False)),

                  path('isbn/<str:isbn>', ISBNDetailView.as_view(), name='isbndetail'),
                  path('isbn', ISBNView.as_view(), name='isbn'),
                  path('overview', CourseView.as_view(), name='courseview.list'),
                  path('overview/<int:msp_key>', CourseViewDetail.as_view(), name='courseview.details')
              ] + pysidian_core_urls

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                      path('translations/', include('rosetta.urls'))
                  ] + urlpatterns
