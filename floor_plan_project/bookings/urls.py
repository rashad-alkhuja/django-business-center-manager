# bookings/urls.py

# --- THIS IS THE CRITICAL FIX: We must import 'path' ---
from django.urls import path
# --------------------------------------------------------

from django.views.generic import TemplateView
from .views import (
    BookingCalendarView, 
    CreateBookingView, 
    ReceptionDashboardView,
    monthly_usage_report_api,
    usage_report_view  # Added this import
)

urlpatterns = [
    # Existing URLs
    path('', BookingCalendarView.as_view(), name='booking-calendar'),
    path('new/', CreateBookingView.as_view(), name='create-booking'),
    path('reception/', ReceptionDashboardView.as_view(), name='reception-dashboard'),
    
    # Updated report URLs with protected view
    path('reports/usage/', usage_report_view, name='usage-report'),
    path('api/reports/usage/', monthly_usage_report_api, name='usage-report-api'),
]