"""
This module contains all the View related logic for any pages the teachers might see. It currently
is more a set of tools which aren't integrated into a fluid process yet
"""
import logging
from typing import Union, Dict, Any

from django.forms import Form
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView

from steambird.models import Teacher, MSP, MSPLineType, Config
from steambird.models.msp import MSPLine
from steambird.perm_utils import IsTeacherMixin
from .forms import PrefilledMSPLineForm, \
    PrefilledSuggestAnotherMSPLineForm

LOGGER = logging.getLogger(__name__)


class HomeView(IsTeacherMixin, View):
    """
    The Homeview for teachers, is still pretty empty and could be improved upon.
    """
    # pylint: disable=no-self-use
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "teacher/home.html")


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
        new_mspline = form.save(commit=False)
        new_mspline.created_by = self.request.user
        new_mspline.created_by_side = "TEACHER"
        new_mspline.save()
        form.save_m2m()
        return super().form_valid(form)

    def form_invalid(self, form):
        LOGGER.warning(
            "Invalid MSPLine create body submitted, with errors: {}",
            form.errors,
        )

        return super().form_invalid(form)

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
