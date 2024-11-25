from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView


class AboutPage(TemplateView):
    """Страница информации о проекте."""

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """Страница правил сайта."""

    template_name = 'pages/rules.html'


class RegistrationView(CreateView):
    """Страница регистрации пользователя."""

    template_name = 'registration/registration_form.html',
    form_class = UserCreationForm,
    success_url = reverse_lazy('pages:about')


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request, reason=''):
    return render(request, 'pages/500.html', status=500)
