from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm


class RegistrationView(CreateView):
    """Регистрация пользователя."""

    template_name = 'registration/registration_form.html',
    form_class = UserCreationForm,
    success_url = reverse_lazy('pages:about')
