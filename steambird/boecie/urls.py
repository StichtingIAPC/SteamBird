from django.urls import path

from steambird.boecie.views import HomeView, StudyDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('study/<int:pk>', StudyDetailView.as_view(), name='study.list'),

]