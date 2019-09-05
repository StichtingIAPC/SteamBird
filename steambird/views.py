from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from steambird.models import AuthToken


def handler404(request, exception=None, template_name="errors/404.html"):
    return render(request, template_name=template_name, status=404, context={
        'exception': exception,
    })


def handler500(request, exception=None, template_name="errors/500.html"):
    return render(request, template_name=template_name, status=500, context={
        'exception': exception,
    })


def permission_denied(request, exception=None, template_name="errors/403.html"):
    return render(request, template_name=template_name, status=403, context={
        'exception': exception,
    })


def bad_request(request, exception=None, template_name="errors/400.html"):
    return render(request, template_name=template_name, status=400, context={
        'exception': exception,
    })


class IndexView(View):
    # pylint: disable=no-self-use
    def get(self, request):
        return render(request, "steambird/index.html")


class TokenLogin(View):
    # pylint: disable=no-self-use
    def get(self, request):
        if 'token' not in request.GET:
            return HttpResponse(status=401, reason="No Credentials Provided")

        try:
            token: AuthToken = AuthToken.objects.get(token=request.GET['token'])
        except AuthToken.DoesNotExist as e:
            return HttpResponse(status=401, reason="Invalid credentials")

        token.last_host = request.META['REMOTE_ADDR']

        login(request, token.user)

        if 'next' in request.GET:
            return HttpResponseRedirect(redirect_to=request.GET['next'])

        return HttpResponseRedirect(redirect_to=reverse('index'))
