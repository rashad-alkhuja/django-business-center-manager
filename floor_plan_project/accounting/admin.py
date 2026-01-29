# accounting/admin.py
from django.contrib import admin
from .models import Lease, Cheque

# This makes the cheques for a lease visible on the lease page itself
class ChequeInline(admin.TabularInline):
    model = Cheque
    extra = 0 # Don't show extra blank forms for adding cheques manually
    readonly_fields = ('due_date', 'amount', 'status') # We can't edit these here
    can_delete = False # We don't want to delete cheques from this view

@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('office', 'company_name', 'start_date', 'end_date', 'annual_rent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('office__office_number', 'company_name')
    # This adds the ChequeInline to the bottom of the Lease detail page
    inlines = [ChequeInline]

    
@admin.register(Cheque)
class ChequeAdmin(admin.ModelAdmin):
    list_display = ('lease', 'due_date', 'amount', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('lease__office__office_number',)