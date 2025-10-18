# offices/forms.py

from django import forms

class ProposalForm(forms.Form):
    proposal_date = forms.DateField(label="Proposal Date", widget=forms.SelectDateWidget)
    company_name = forms.CharField(label="Company Name", max_length=200)
    phone_number = forms.CharField(label="Phone Number", max_length=50)
    
    # We can add more fields from the proposal here if needed
    proposed_lease_term = forms.CharField(initial="1 year", max_length=50)
    annual_rent = forms.IntegerField(label="Annual Rent (AED)")
    security_deposit = forms.CharField(initial="5%", max_length=20)
    admin_fees = forms.IntegerField(label="Admin Fees (AED)", initial=250)