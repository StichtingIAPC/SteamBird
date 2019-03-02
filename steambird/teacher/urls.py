from django.urls import path

from steambird.teacher.views import AddMSPView, ISBNSearchApiView

urls = ([
    path('/book/new', AddMSPView.as_view(), name='msp.new'),
    path('/api/isbn/search', ISBNSearchApiView.as_view(), name='isbn.search'),
], 'teacher')
