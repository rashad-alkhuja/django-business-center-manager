from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'

    def ready(self):
        from django.contrib.auth.models import Group
        
        # Define the roles for the application (removed 'Tenant' role)
        groups = ["Manager", "Reception", "Accountant"]
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
