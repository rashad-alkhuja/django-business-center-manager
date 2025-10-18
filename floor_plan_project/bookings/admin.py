# bookings/admin.py
from django.contrib import admin
from .models import MeetingRoom, Booking

@admin.register(MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_room', 'start_time', 'end_time', 'booked_by')
    list_filter = ('meeting_room', 'start_time')
    search_fields = ('title', 'booked_by__username')