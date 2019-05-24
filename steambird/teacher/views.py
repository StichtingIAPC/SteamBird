from json import dumps

from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView

from steambird.models import Teacher, MSP, MSPLineType
from steambird.models_msp import MSPLine
from steambird.perm_utils import IsTeacherMixin
from steambird.teacher.tools import isbn_lookup
from .forms import ISBNForm, PrefilledMSPLineForm, \
    PrefilledSuggestAnotherMSPLineForm, BookForm, ScientificPaperForm


class HomeView(IsTeacherMixin, View):

    # pylint: disable=no-self-use
    def get(self, request):
        return render(request, "steambird/teacher/home.html")


class ISBNView(IsTeacherMixin, FormView):
    form_class = ISBNForm
    template_name = 'steambird/teacher/ISBN.html'

    def form_valid(self, form):
        isbn = form.data['isbn']
        return redirect(reverse('teacher:isbndetail', kwargs={'isbn': isbn}))

    def form_invalid(self, form):
        return render(self.request, 'steambird/teacher/ISBN.html', {'form': form})


class ISBNDetailView(IsTeacherMixin, View):
    def get(self, _request, isbn):
        isbn_data = isbn_lookup(isbn)
        result = {'book': isbn_data}

        if isbn_data is None:
            result = {'retrieved_data': "No data was found for given ISBN"}

        return render(self.request, 'steambird/teacher/book.html', result)


class AddMSPView(IsTeacherMixin, View):
    def get(self, _request):
        return render(self.request, 'steambird/new_book.html')

    # pylint: disable=no-self-use
    def post(self, request):
        material_type = request.POST.get('type')

        # Set all book related variables
        if material_type == 'book':
            form = BookForm(request.POST)
            reverse_url = 'teacher:isbndetail'
            kwargs = {'isbn': request.POST.get('ISBN')}
        # Set all paper related variables
        elif material_type == 'paper':
            form = ScientificPaperForm(request.POST)
            reverse_url = 'teacher:isbndetail'  # TODO: Replace by ScientificArticle URL
            kwargs = {'isbn': request.POST.get('doi')}  # TODO: Replace by ScientificArticle URL
        # Type is not supported
        else:
            return HttpResponseBadRequest()

        if form.is_valid():
            form.save()
            return redirect(reverse(reverse_url, kwargs=kwargs))

        return render(request, 'steambird/new_book.html', {'form': form})


class ISBNSearchApiView(View):
    # pylint: disable=no-self-use
    def get(self, request):
        isbn = request.GET['isbn']
        isbn_data = isbn_lookup(isbn)

        if isbn_data is None:
            return HttpResponseNotFound(
                dumps(str("No data was found for given ISBN")),
                content_type="application/json",
            )

        return JsonResponse(isbn_data)


class CourseView(IsTeacherMixin, TemplateView):
    template_name = 'steambird/teacher/courseoverview.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        try:
            data["teacher"] = Teacher.objects.get(user=self.request.user)
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

    template_name = "steambird/teacher/msp/detail.html"
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

    def form_valid(self, form):
        """
        Makes sure the data is saved after submission.

        :param form: The form and its data.
        :return: a redirect to get_success_url.
        """
        form.save(commit=True)
        return super().form_valid(form)

    def get_initial(self):
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

    def get_context_data(self, **kwargs):
        """
        Constructs the context (apart from the primary form). This means that it
        will generate all secondary forms, and meta data for allowing proper
        and nice-looking renderings of the view.

        :param kwargs: ¯\\_(ツ)_/¯
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
