import logging
from json import dumps
from typing import Union, Any, Optional
from urllib.parse import quote, unquote

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpRequest, \
    HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, DetailView
from django_addanother.views import CreatePopupMixin

from steambird.material_management.forms import ISBNForm, BookForm, ScientificPaperForm, \
    OtherMaterialForm
from steambird.material_management.tools import isbn_lookup, doi_lookup
from steambird.models import Book, ScientificArticle, OtherMaterial
from steambird.util import MultiFormView


LOGGER = logging.getLogger(__name__)


class ISBNView(LoginRequiredMixin, FormView):
    """
    Original ISBN lookup view written pre 'Add Material' option. Still does the lookup, usage
    should be discouraged for anything else than testing purposes.
    """

    form_class = ISBNForm
    template_name = 'material_management/ISBN.html'

    def form_valid(self, form: Form) -> HttpResponseRedirect:
        isbn = form.data['isbn']
        return redirect(reverse('material_management:isbnlookup', kwargs={'isbn': isbn}))

    def form_invalid(self, form: Form) -> HttpResponse:
        return render(self.request, 'material_management/ISBN.html', {'form': form})


class ISBNLookupView(LoginRequiredMixin, View):
    """
    A view which does a lookup based on the isbn givin in the URL. Does not show requested isbn's
    stored info if we have any. For that, use :any:`ISBNDetailView`
    """
    def get(self, _request, isbn):
        isbn_data = isbn_lookup(isbn)
        result = {'book': isbn_data}

        if isbn_data is None:
            result = {'retrieved_data': "No data was found for given ISBN"}

        return render(self.request, 'material_management/book.html', result)


class AddMaterialView(LoginRequiredMixin, CreatePopupMixin, MultiFormView):
    """
    View which shows the choice-menu and handles what happens with post-data. Creates a new Material
     object of chosen type
    """

    forms = {
        'book': BookForm,
        'paper': ScientificPaperForm,
        'other': OtherMaterialForm,
    }

    template_name = 'material_management/new_studymaterial.html'

    form_name_field_name = 'object_type'

    # noinspection PyMethodOverriding
    # pylint: disable=arguments-differ,unused-argument, logging-format-interpolation
    def form_valid(self, request: HttpRequest, form: Form, form_name: str) -> Optional[Any]:
        obj = form.save()

        if isinstance(form, BookForm):
            reverse_url = 'material_management:isbndetail'
            kwargs = {'isbn': request.POST.get('ISBN')}
        elif isinstance(form, ScientificPaperForm):
            reverse_url = 'material_management:articledetail'
            kwargs = {'doi': quote(request.POST.get('DOI'), safe='')}
        elif isinstance(form, OtherMaterialForm):
            reverse_url = 'material_management:otherdetail'
            kwargs = {'pk': obj.pk}
        else:
            LOGGER.warning(
                'Form of unknown type was submitted to material create, namely:'
                ' {}.'.format(obj.__class__.__name__))
            return HttpResponseBadRequest()

        if self.is_popup():
            self.respond_script(obj)

        return redirect(reverse(reverse_url, kwargs=kwargs))


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
    template_name = 'material_management/bookdetail.html'

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
    template_name = 'material_management/DOI.html'

    def get_object(self, queryset=None) -> Union[QuerySet, ObjectDoesNotExist]:
        """
        Get the object for the view to display. kwargs['doi'] should be a quoted verion of the ODI

        :param queryset:
        :return: Queryset or EmptyQueryset
        """
        queryset = queryset or ScientificArticle
        doi = unquote(self.kwargs['doi'])
        return queryset.objects.get(DOI=doi)


class OtherDetailView(LoginRequiredMixin, DetailView):

    model = OtherMaterial
    template_name = 'material_management/other_material.html'
    context_object_name = 'material'
