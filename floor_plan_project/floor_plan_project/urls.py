# floor_plan_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import DashboardView

urlpatterns = [
    # The admin URL correctly lives here in the main project router.
    path('secure-admin/', admin.site.urls),
    
    path('', DashboardView.as_view(), name='dashboard'),
    path('floor-plan/', include('offices.urls')),
    path('bookings/', include('bookings.urls')), # This line includes the corrected file above.
    
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]