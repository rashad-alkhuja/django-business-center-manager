from django.db import models
from django.contrib.auth.models import User
from offices.models import Office
import uuid

class MeetingRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name

class Booking(models.Model):
    meeting_room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name="bookings")
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    associated_office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, blank=True, related_name="meeting_room_bookings")
    recurrence_id = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f'"{self.title}" in {self.meeting_room.name} from {self.start_time.strftime("%Y-%m-%d %H:%M")}'

    class Meta:
        ordering = ['start_time']