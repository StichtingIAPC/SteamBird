from typing import ClassVar, Dict, Type, Any, Optional

from django import views
from django.forms import Form, CharField, HiddenInput
from django.http import HttpRequest


class MultiFormView(views.generic.TemplateView):
    forms: ClassVar[Dict[str, Type[Form]]] = {}
    """
    Dictionary of form_name->form class. These are the forms that should be
    shown on this page.
    """

    form_name_field_name: ClassVar[str] = '__form_name'

    def get_object_for(self,
                       form_name: str,
                       request: HttpRequest) -> Optional[Any]:
        """
        Callback to get object in case of edit views.

        :param form_name:
        :param request:
        :return:
        """

    def form_valid(self, request: HttpRequest, form: Form, form_name: str):
        """
        Callback for a post request that sent valid form data.

        :param request: The request that was received.
        :param form: The form that was valid.
        :param form_name: The name of the form that was filled out.
        :return: Nothing
        """

    def form_invalid(self, request: HttpRequest, form: Form, form_name: str):
        """
        Callback for a post request that sent invalid data.

        :param request: The request that was received.
        :param form: The form that was invalid.
        :param form_name: The name of the form that was filled out.
        :return: Nothing
        """

    def get_forms_classes(self) -> Dict[str, Type[Form]]:
        """
        If the forms that are in the view depend on the request, or another
        state, this function can be overridden to return custom forms.

        :return Dict[str, Type[Form]]: Forms that should be shown in the view.
        """
        return self.__class__.forms

    def _set_form_meta_fields(self, forms: Dict[str, Form]):
        for name, form in forms.items():
            form.fields[self.__class__.form_name_field_name] = CharField(
                widget=HiddenInput, initial=name)

    def get_form_instances(self,
                           forms: Dict[str, Type[Form]],
                           request: HttpRequest,
                           with_data: bool = False) -> Dict[str, Form]:
        """
        Instantiates the form classes, potentially with edit data, or data that
        was submitted in the request.

        :param forms: The forms that should be shown in this view
        :param request: The request that was received, for which a response with
                    forms should be formulated.
        :param with_data: Whether to update each form with data of pre-existing
                    objects, if the forms are meant to be used as update forms.
        :return Dict[str, Form]: A dictionary of instantiated forms.
        """
        post_data = request.POST or None

        rv = {}

        for name, form in forms.items():
            if with_data:
                obj = self.get_object_for(name, request)
                if obj:
                    rv[name] = form(post_data, prefix=name, instance=obj)
                    continue
            rv[name] = form(post_data, prefix=name)

        return rv

    def handle_post_forms(self, request, forms):
        """
        Fork to the validation functions in case of form submissions.

        :param request: The POST request that was received with form data.
        :param forms: The forms that were shown on this page.
        :return: Nothing
        """
        if not request.POST:
            return

        form_name = request.POST[self.__class__.form_name_field_name]
        form = forms[form_name]

        if not form:
            return

        if form.is_valid():
            self.form_valid(request, form, form_name)
        else:
            self.form_invalid(request, form, form_name)

    def get_context_data(self, forms=None, **kwargs):
        if not forms:
            forms = self.get_form_instances(
                self.get_forms_classes(), self.request)

        context = {
            **super().get_context_data(**kwargs),
            **forms,
        }

        return context

    def post(self, request):
        forms = self.get_form_instances(self.get_forms_classes(), request)
        context = self.get_context_data(forms=forms)

        self.handle_post_forms(request, forms)

        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        forms = self.get_form_instances(self.get_forms_classes(), request, with_data=True)
        context = self.get_context_data(forms=forms)

        return self.render_to_response(context)
