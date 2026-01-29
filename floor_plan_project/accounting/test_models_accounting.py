from django.test import TestCase
from django.utils import timezone
from offices.models import Office
from accounting.models import Lease, Cheque
import datetime

class AccountingLeaseTests(TestCase):
    def setUp(self):
        self.office = Office.objects.create(
            office_number=201,
            size_sqft=400.0,
            annual_rent=40000,
            status='available'
        )

    def test_multiple_leases_for_one_office(self):
        # Create first lease
        lease1 = Lease.objects.create(
            office=self.office,
            company_name="Company A",
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 12, 31),
            annual_rent=40000,
            number_of_cheques=4,
            is_active=False
        )
        
        # Create second lease
        lease2 = Lease.objects.create(
            office=self.office,
            company_name="Company B",
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 12, 31),
            annual_rent=42000,
            number_of_cheques=4,
            is_active=True
        )

        self.assertEqual(self.office.leases.count(), 2)
        # Check cheque generation for each lease
        self.assertEqual(lease1.cheques.count(), 4)
        self.assertEqual(lease2.cheques.count(), 4)
        
    def test_active_leases_filtering(self):
        Lease.objects.create(
            office=self.office,
            company_name="Old Tenant",
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            annual_rent=30000,
            is_active=False
        )
        Lease.objects.create(
            office=self.office,
            company_name="New Tenant",
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 12, 31),
            annual_rent=35000,
            is_active=True
        )
        
        active_leases = Lease.objects.filter(is_active=True)
        self.assertEqual(active_leases.count(), 1)
        self.assertEqual(active_leases[0].company_name, "New Tenant")
