# offices/serializers.py

from rest_framework import serializers
from .models import Office

class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        # --- ADD 'expiry_date' TO THIS LIST ---
        fields = ['office_number', 'size_sqft', 'annual_rent', 'status', 'expiry_date',
        'company_name', 'contact_person', 'contact_email', 'contact_phone'
        ]
        # ------------------------------------

