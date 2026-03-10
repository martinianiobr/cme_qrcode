from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from materiais import views
from materiais.forms import LoginForm

urlpatterns = [
    path('admin/', admin.site.urls),

    # login/logout
    path('login/', auth_views.LoginView.as_view(template_name='materiais/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # dashboard inicial
    path('', views.dashboard, name='dashboard'),

    # rotas do app
    path('', include('materiais.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
