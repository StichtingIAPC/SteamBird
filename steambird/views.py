from django.http import HttpResponseServerError, HttpResponseNotFound, HttpResponseForbidden, \
    HttpResponseBadRequest
from django.shortcuts import render, render_to_response
from django.views import View
from django.views.defaults import page_not_found


def handler404(request, exception, template_name="404.html"):
    return page_not_found(request, exception, template_name="errors/404.html")


def handler500(request, template_name="500.html"):
    response = render_to_response("errors/500.html")
    response.status_code = 500
    return response

#
# def permission_denied(request, exception):
#     return HttpResponseForbidden(render(request, 'errors/403.html'))
#     # return render(request, 'errors/403.html', status=403)
#
#
# def bad_request(request, exception):
#     return HttpResponseBadRequest(render(request, 'errors/400.html'))
#     # return render(request, 'errors/400.html', status=400)


class IndexView(View):
    # pylint: disable=no-self-use
    def get(self, request):
        return render(request, "steambird/index.html")
