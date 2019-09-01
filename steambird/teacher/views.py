"""
This module contains all the View related logic for any pages the teachers might see. It currently
is more a set of tools which aren't integrated into a fluid process yet
"""
import logging
from json import dumps
from typing import Union, Dict, Any
from urllib.parse import quote, unquote

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.forms import Form
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, \
    HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView, DetailView

from steambird.models import Teacher, MSP, MSPLineType, ScientificArticle, Config, Book
from steambird.models.msp import MSPLine
from steambird.perm_utils import IsTeacherMixin
from steambird.teacher.tools import isbn_lookup, doi_lookup
from .forms import ISBNForm, PrefilledMSPLineForm, \
    PrefilledSuggestAnotherMSPLineForm, BookForm, ScientificPaperForm


LOGGER = logging.getLogger(__name__)


class HomeView(IsTeacherMixin, View):
    """
    The Homeview for teachers, is still pretty empty and could be improved upon.
    """
    # pylint: disable=no-self-use
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "teacher/home.html")


class ISBNView(IsTeacherMixin, FormView):
    """
    Original ISBN lookup view written pre 'Add Material' option. Still does the lookup, usage
    should be discouraged for anything else than testing purposes.
    """

    form_class = ISBNForm
    template_name = 'teacher/ISBN.html'

    def form_valid(self, form: Form) -> HttpResponseRedirect:
        isbn = form.data['isbn']
        return redirect(reverse('isbnlookup', kwargs={'isbn': isbn}))

    def form_invalid(self, form: Form) -> HttpResponse:
        return render(self.request, 'teacher/ISBN.html', {'form': form})


class ISBNLookupView(IsTeacherMixin, View):
    """
    A view which does a lookup based on the isbn givin in the URL. Does not show requested isbn's
    stored info if we have any. For that, use :any:`ISBNDetailView`
    """
    def get(self, _request, isbn):
        isbn_data = isbn_lookup(isbn)
        result = {'book': isbn_data}

        if isbn_data is None:
            result = {'retrieved_data': "No data was found for given ISBN"}

        return render(self.request, 'teacher/book.html', result)


class AddMaterialView(IsTeacherMixin, View):
    """
    View which shows the choice-menu and handles what happens with post-data. Creates a new Material
     object of chosen type
    """
    def get(self, _request) -> HttpResponse:
        return render(self.request, 'teacher/new_studymaterial.html')

    # pylint: disable=no-self-use
    def post(self, request) -> Union[HttpResponseBadRequest, HttpResponseRedirect, HttpResponse]:
        """
        This method handles all the responses which might be submitted using the template, fills in
        the form and validates it before returning a specific return url. Take care when working
        with the DOI, as this is quoted to be safe to handled on post. Unquoted DOI's will break
        and fail due to the use of '/' in them

        :param request: Probably a Django HttpRequest
        :return: Bad request or a redirect to the page the right data, or a response with errors
        """
        material_type = request.POST.get('type')

        # Set all book related variables
        if material_type == 'book':
            form = BookForm(request.POST)
            reverse_url = 'teacher:isbndetail'
            kwargs = {'isbn': request.POST.get('ISBN')}
        # Set all paper related variables
        elif material_type == 'paper':
            form = ScientificPaperForm(request.POST)
            reverse_url = 'teacher:articledetail'
            kwargs = {'doi': quote(request.POST.get('DOI'), safe='')}
        # Type is not supported
        else:
            return HttpResponseBadRequest()

        if form.is_valid():
            form.save()
            return redirect(reverse(reverse_url, kwargs=kwargs))

        return render(request, 'teacher/new_studymaterial.html', {'form': form})


class ISBNSearchApiView(LoginRequiredMixin, View):
    """
    The 'API endpoint' view we use for retrieving data concerning books. It returns a JsonResponse
    with the data found on the isbn parameter.
    """

    # pylint: disable=no-self-use
    def get(self, request: HttpRequest) -> Union[HttpResponseNotFound, JsonResponse]:
        """
        Makes a call to the isbn_lookup tool which either returns a JSON response of data, or
        returns a HttpResponseNotFound if nothing can be found

        :param request: HttpRequest Object
        :return: Either a response, or the string "No data was found for given ISBN"
        """
        isbn = request.GET['isbn']
        isbn_data = isbn_lookup(isbn)

        if isbn_data is None:
            return HttpResponseNotFound(
                dumps(str("No data was found for given ISBN")),
                content_type="application/json",
            )

        return JsonResponse(isbn_data)


class ISBNDetailView(LoginRequiredMixin, DetailView):
    """
    Shows details we have stored on a given ISBN. Can return an error when object does not exist
    """
    model = Book
    template_name = 'teacher/bookdetail.html'

    def get_object(self, queryset=None):
        queryset = queryset or Book
        isbn = self.kwargs['isbn']
        return queryset.objects.get(ISBN=isbn)


class DOISearchApiView(LoginRequiredMixin, View):
    """
    The 'API endpoint' view  we use for retrieving data concerning Scientific articles. It returns a
    JsonResponse with the data found on the DOI parameter
    """

    # pylint: disable=no-self-use
    def get(self, request: HttpRequest) -> Union[HttpResponseNotFound, JsonResponse]:
        """
        Method which makes a call to the doi_lookup tool. Retrieves a lot of data, which all
        returned and sifted through on the front-end

        :param request: HttpRequest object
        :return: Either a HttpResponseNotFound or a JsonResponse if successful
        """
        doi = request.GET['doi']
        doi_data = doi_lookup(doi)

        if doi_data is None:
            return HttpResponseNotFound(
                dumps(str("No data was found for given ISBN")),
                content_type="application/json",
            )

        return JsonResponse(doi_data)


class DOIDetailView(LoginRequiredMixin, DetailView):
    """
    View which presents the object related the doi passed on in the kwargs. DOI needs to be safe to
    be handled, meaning it should be quoted before passing on to this view. This is due to '/' in
    DOI's
    """
    model = ScientificArticle
    template_name = 'teacher/DOI.html'

    def get_object(self, queryset=None) -> Union[QuerySet, ObjectDoesNotExist]:
        """
        Get the object for the view to display. kwargs['doi'] should be a quoted verion of the ODI

        :param queryset:
        :return: Queryset or EmptyQueryset
        """
        queryset = queryset or ScientificArticle
        doi = unquote(self.kwargs['doi'])
        return queryset.objects.get(DOI=doi)


class CourseView(IsTeacherMixin, TemplateView):
    """
    View which returns a list with all courses a teacher gives. Currently has no filters for
    coordinators or teachers, and just works on the teachers ID
    """
    template_name = 'teacher/courseoverview.html'

    def get_context_data(self, **kwargs) -> Union[Dict[str, Any], Http404]:
        """
        Method to get and setup context data. Retrieves all courses of the current active period and
        return them in a list.

        :param kwargs: Dict object
        :return:
        """
        data = super().get_context_data(**kwargs)

        data['year'] = Config.get_system_value('year')
        data['period'] = Config.get_system_value('period')

        try:
            data['teacher'] = Teacher.objects.get(user=self.request.user)
            data['courses'] = data["teacher"].all_courses_period(
                year=data['year'],
                period=data['period']
            )
        except Teacher.DoesNotExist:
            raise Http404

        return data


class MSPDetail(IsTeacherMixin, FormView):
    """
    This is quite a complex view. It extends a form view, as its primary action
    is the creation of MSP lines. Even though this view uses multiple forms,
    only one type of form can be saved. This is fine, since all forms in this
    view concern the same data-structure.
    """

    template_name = "teacher/msp/detail.html"
    form_class = PrefilledSuggestAnotherMSPLineForm

    def get_success_url(self):
        """
        Makes sure that the view returns to the MSP overview after submission
        of a form.

        :return: the URL that points to the current view.
        """
        return reverse('teacher:msp.detail', kwargs={
            'pk': self.kwargs.get("pk"),
        })

    def form_valid(self, form: Form) -> HttpResponseRedirect:
        """
        Makes sure the data is saved after submission.

        :param form: The form and its data.
        :return: a redirect to get_success_url.
        """
        form.save(commit=True)
        return super().form_valid(form)

    def get_initial(self) -> dict:
        """
        Fills in initial data for the primary form. The primary form is the
        form at the bottom of the page, where the teacher can request other
        study materials if need be.

        :return: Initial form data
        """
        initial = super().get_initial()
        initial["msp"] = self.kwargs.get("pk")
        initial["type"] = MSPLineType.request_material.name

        return initial

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs the context (apart from the primary form). This means that it
        will generate all secondary forms, and meta data for allowing proper
        and nice-looking renderings of the view.

        :param kwargs: Dict of any kwargs passed as defined in the URL listing
        :return: a context
        """
        try:
            msp = MSP.objects.get(pk=self.kwargs.get("pk"))
        except MSPLine.DoesNotExist:
            raise Http404

        data = super().get_context_data(**kwargs)
        # The main MSP
        data["msp"] = msp
        # List of MSPLines with metadata
        data["lines"] = []
        # Tracks whether the last line is a approve_material line.
        data["finished"] = False

        # Tracks the line that is the last "set_available_materials" line.
        last_available = {"last_available": False}
        for line in msp.mspline_set.all():
            data["lines"].append({
                "line": line,
                "materials": [],
            })

            if line.type == MSPLineType.set_available_materials.name:
                # Swaps the last_available MSPLine of type available_materials
                # to the current line.
                last_available["last_available"] = False
                last_available = data["lines"][-1]
                last_available["last_available"] = True

            for material in line.materials.all():
                data["lines"][-1]["materials"].append({
                    "material": material
                })

                if line.type == 'set_available_materials':
                    data["lines"][-1]["materials"][-1]["form"] = \
                        PrefilledMSPLineForm({
                            "msp": msp.pk,
                            "comment": "",
                            "materials": [material.pk],
                            "type": "approve_material",
                        })

                # Tracks whether this MSP is finished.
                if line.type == MSPLineType.approve_material.name:
                    data["finished"] = True
                else:
                    data["finished"] = False

        return data
