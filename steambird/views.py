from django.shortcuts import render
from django.views import View


def handler404(request, exception=None, template_name="404.html"):
    return render(request, template_name=template_name, status=404, context={
        'exception': exception,
    })


def handler500(request, exception=None, template_name="500.html"):
    return render(request, template_name=template_name, status=500, context={
        'exception': exception,
    })


def permission_denied(request, exception=None, template_name="403.html"):
    return render(request, template_name=template_name, status=403, context={
        'exception': exception,
    })


def bad_request(request, exception=None, template_name="400.html"):
    return render(request, template_name=template_name, status=400, context={
        'exception': exception,
    })


class IndexView(View):
    # pylint: disable=no-self-use
    def get(self, request):
        return render(request, "steambird/index.html")
