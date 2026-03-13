from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from materiais import views
from materiais.views_kitpaciente import dashboard_kit_paciente
from materiais.forms import LoginForm

admin.site.site_header = 'CME QRCode - Administração'
admin.site.site_title = 'CME QRCode Admin'
admin.site.index_title = 'Painel Administrativo'

urlpatterns = [
    path('admin/', admin.site.urls),

    # login/logout
    path('login/', auth_views.LoginView.as_view(template_name='materiais/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # dashboard inicial
    path('', dashboard_kit_paciente, name='dashboard'),

    # rotas do app
    path('', include('materiais.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
