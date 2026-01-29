# bookings/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F, ExpressionWrapper, DurationField, Sum, Q
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
import uuid

from .models import MeetingRoom, Booking
from .forms import BookingForm
from offices.models import Office

def is_manager_or_reception(user):
    """Helper function to check if user is manager or reception"""
    return user.is_superuser or user.groups.filter(name__iregex=r'^(Manager|Reception)$').exists()

# --- THIS VIEW HAS BEEN COMPLETELY REWRITTEN FOR ACCURACY AND EFFICIENCY ---
class BookingCalendarView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        rooms = MeetingRoom.objects.all()
        today = timezone.localdate() # Use timezone-aware local date

        # Get the day from the query parameter, default to today
        day_str = request.GET.get('day', today.isoformat())
        try:
            current_day = datetime.date.fromisoformat(day_str)
        except ValueError:
            current_day = today

        # Calculate week boundaries based on the current day
        start_of_week = current_day - datetime.timedelta(days=current_day.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
        
        # Navigation links for previous and next week
        prev_week = start_of_week - datetime.timedelta(days=7)
        next_week = start_of_week + datetime.timedelta(days=7)

        # Get all bookings for the visible week
        bookings_this_week = Booking.objects.filter(
            start_time__date__gte=start_of_week,
            start_time__date__lte=end_of_week
        ).order_by('start_time')

        # --- PRE-PROCESSING LOGIC ---
        # Create a structured dictionary to make the template extremely simple
        calendar_data = {room: {day: [] for day in [start_of_week + datetime.timedelta(days=i) for i in range(7)]} for room in rooms}
        
        for booking in bookings_this_week:
            room = booking.meeting_room
            day = booking.start_time.date()
            if room in calendar_data and day in calendar_data[room]:
                calendar_data[room][day].append(booking)
        
        context = {
            'calendar_data': calendar_data,
            'days_of_week': [start_of_week + datetime.timedelta(days=i) for i in range(7)],
            'prev_week_url': f"?day={prev_week.isoformat()}",
            'next_week_url': f"?day={next_week.isoformat()}",
            'current_week_str': f"{start_of_week.strftime('%d %b')} - {end_of_week.strftime('%d %b %Y')}"
        }
        return render(request, 'bookings/booking_calendar.html', context)

# --- (The rest of the views remain the same) ---
class CreateBookingView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        form = BookingForm(user=request.user)
        return render(request, 'bookings/create_booking.html', {'form': form})

    def post(self, request):
        form = BookingForm(request.POST, user=request.user)
        
        if form.is_valid():
            # Get the cleaned data from the form
            recurrence = form.cleaned_data.get('recurrence')
            end_recurrence = form.cleaned_data.get('end_recurrence')
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')
            
            # This list will hold all the booking objects we need to create
            bookings_to_create = []

            # --- CASE 1: This is a single, non-recurring booking ---
            if recurrence == 'none' or not end_recurrence:
                new_booking = form.save(commit=False)
                new_booking.booked_by = request.user

                # If this user is the contact person for an office, set associated office
                tenant_office = Office.objects.filter(contact_person=request.user).first()
                if tenant_office and not new_booking.associated_office:
                    new_booking.associated_office = tenant_office

                bookings_to_create.append(new_booking)

            # --- CASE 2: This is a recurring booking ---
            else:
                current_start = start_time
                current_end = end_time
                delta = datetime.timedelta(days=7) if recurrence == 'weekly' else datetime.timedelta(days=1)
                new_recurrence_id = uuid.uuid4()
                
                while current_start.date() <= end_recurrence:
                    new_booking = Booking(
                        meeting_room=form.cleaned_data.get('meeting_room'),
                        booked_by=request.user,
                        title=form.cleaned_data.get('title'),
                        start_time=current_start,
                        end_time=current_end,
                        recurrence_id=new_recurrence_id
                    )

                    # If this user is the contact person for an office, set associated office
                    tenant_office = Office.objects.filter(contact_person=request.user).first()
                    if tenant_office:
                        new_booking.associated_office = tenant_office

                    # If manager selected an office, use that instead
                    if form.cleaned_data.get('associated_office'):
                        new_booking.associated_office = form.cleaned_data.get('associated_office')

                    bookings_to_create.append(new_booking)
                    current_start += delta
                    current_end += delta

            # Save all bookings at once
            Booking.objects.bulk_create(bookings_to_create)
            return redirect('booking-calendar')
        
        return render(request, 'bookings/create_booking.html', {'form': form})

class ReceptionDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__iregex=r'^(Manager|Reception)$').exists()
    
    def handle_no_permission(self):
        return redirect('dashboard')
        
    def get(self, request):
        now = timezone.now()
        
        # Optimize query by using select_related for related fields
        upcoming_bookings = Booking.objects.filter(start_time__gte=now).select_related(
            'meeting_room', 
            'associated_office', 
            'booked_by'
        ).order_by('start_time')
        
        context = {'upcoming_bookings': upcoming_bookings}
        return render(request, 'bookings/reception_dashboard.html', context)

@login_required(login_url='/login/')
@user_passes_test(is_manager_or_reception, login_url='/dashboard/')
def usage_report_view(request):
    return render(request, 'bookings/usage_report.html')

@api_view(['GET'])
@login_required
def monthly_usage_report_api(request):
    """
    Calculates the total meeting room hours booked per office for the current month.
    """
    # Check permissions
    if not is_manager_or_reception(request.user):
        return Response({'error': 'Permission denied'}, status=403)
        
    today = timezone.localdate()
    
    # Get all offices
    offices = Office.objects.all().order_by('office_number')

    # Calculate the total duration of bookings for each office in the current month
    usage_data = offices.annotate(
        # Calculate duration of each booking: end_time - start_time
        booking_duration=ExpressionWrapper(
            F('meeting_room_bookings__end_time') - F('meeting_room_bookings__start_time'), 
            output_field=DurationField()
        ),
        # Sum up the durations, but only for bookings in the current month
        total_hours_this_month=Coalesce(
            Sum(
                'booking_duration',
                filter=Q(
                    meeting_room_bookings__start_time__month=today.month,
                    meeting_room_bookings__start_time__year=today.year
                )
            ),
            datetime.timedelta(0)
        )
    ).values('office_number', 'total_hours_this_month')
    
    # Convert timedelta to total hours for easier display
    report = []
    for item in usage_data:
        total_seconds = item['total_hours_this_month'].total_seconds()
        report.append({
            'office_number': item['office_number'],
            'total_hours': round(total_seconds / 3600, 2)  # Convert seconds to hours
        })

    return Response(report)