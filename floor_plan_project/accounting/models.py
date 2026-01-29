# accounting/models.py

from django.db import models
from offices.models import Office
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from dateutil.relativedelta import relativedelta

class Lease(models.Model):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name="leases")
    company_name = models.CharField(max_length=200, blank=True, null=True)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    annual_rent = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_cheques = models.PositiveIntegerField(default=4)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"Lease for {self.office}"

class Cheque(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),      # Not yet due
        ('Due', 'Due for Deposit'),  # Date has arrived
        ('Deposited', 'Deposited'),  # Submitted to the bank
        ('Cleared', 'Cleared'),      # Funds received
        ('Bounced', 'Bounced'),      # Cheque returned
    ]

    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name="cheques")
    cheque_number = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # For tracking who updated the status and when
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cheque for {self.lease.office} - {self.amount} due {self.due_date}"

    class Meta:
        ordering = ['due_date']

@receiver(post_save, sender=Lease)
def create_cheques_for_new_lease(sender, instance, created, **kwargs):
    """
    This function is automatically called by Django after a Lease is saved.
    'created' will be True if it's a brand new lease.
    """
    # We only want to run this logic ONE TIME, when the lease is first created.
    if created:
        lease = instance
        num_cheques = lease.number_of_cheques

        # Safety check: if there are no cheques, do nothing.
        if num_cheques == 0:
            return

        cheque_amount = lease.annual_rent / num_cheques
        
        # Calculate the interval between cheques (e.g., 12 months / 4 cheques = 3 months apart)
        interval_months = 12 // num_cheques
        
        cheques_to_create = []
        for i in range(num_cheques):
            # Calculate the due date for each cheque
            due_date = lease.start_date + relativedelta(months=i * interval_months)
            
            # Prepare a new Cheque object (but don't save it yet)
            cheque = Cheque(
                lease=lease,
                due_date=due_date,
                amount=cheque_amount,
                status='Pending' # All new cheques start as Pending
            )
            cheques_to_create.append(cheque)

        # Save all the new cheque objects to the database in one efficient operation
        Cheque.objects.bulk_create(cheques_to_create)