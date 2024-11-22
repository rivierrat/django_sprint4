from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path('admin/',
         admin.site.urls),
    path('auth/',
         include('django.contrib.auth.urls')),
    path('auth/registration/',
         views.RegistrationView.as_view(),
         name='registration',),
    path('pages/',
         include('pages.urls')),
    path('',
         include('blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
