from django.shortcuts import render
from django.views import View


class IndexView(View):
    """
    Landing page for the site. Nothing fancy
    """
    # pylint: disable=no-self-use
    def get(self, request):
        return render(request, "steambird/index.html")
