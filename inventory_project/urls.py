from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from inventory import views as inventory_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inventory/', include('inventory.urls')),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', inventory_views.logout_view, name='logout'),
]