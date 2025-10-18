# bookings/forms.py
from django import forms
from .models import Booking, MeetingRoom
from offices.models import Office
from django.core.exceptions import ValidationError
import datetime

class BookingForm(forms.ModelForm):
    # Field for recurrence logic
    RECURRENCE_CHOICES = [
        ('none', 'Does not repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    recurrence = forms.ChoiceField(choices=RECURRENCE_CHOICES, required=False)
    end_recurrence = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = Booking
        fields = ['meeting_room', 'associated_office', 'title', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        # Pop the 'user' argument we will pass from the view
        user = kwargs.pop('user', None)
        super(BookingForm, self).__init__(*args, **kwargs)

        # Make the office dropdown show office numbers instead of "Office object (X)"
        self.fields['associated_office'].queryset = Office.objects.all().order_by('office_number')
        self.fields['associated_office'].label_from_instance = lambda obj: f"Office {obj.office_number}"

        # If the user is a regular tenant, hide the 'associated_office' field
        if user and user.groups.filter(name='Tenant').exists():
            del self.fields['associated_office']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        meeting_room = cleaned_data.get('meeting_room')

        if start_time and end_time and meeting_room:
            # Check if start time is before end time
            if start_time >= end_time:
                raise ValidationError("End time must be after start time.")

            # --- CRITICAL: Double-booking prevention logic ---
            overlapping_bookings = Booking.objects.filter(
                meeting_room=meeting_room,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(pk=self.instance.pk) # Exclude self if updating

            if overlapping_bookings.exists():
                raise ValidationError(
                    f"This time slot in '{meeting_room.name}' is already booked. Please choose a different time."
                )
        return cleaned_data