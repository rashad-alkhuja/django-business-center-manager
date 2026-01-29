# offices/forms.py

from django import forms
import datetime

class ProposalForm(forms.Form):
    company_name = forms.CharField(label="Company Name", max_length=200)
    phone_number = forms.CharField(label="Phone Number", max_length=50)
    
    proposal_date = forms.DateField(
        label="Proposal Date",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today  # Set the default value to today
    )
    
    proposed_lease_term = forms.CharField(initial="1 year", max_length=50)
    annual_rent = forms.IntegerField(label="Annual Rent (AED)")
    security_deposit = forms.CharField(initial="5%", max_length=20)
    admin_fees = forms.IntegerField(label="Admin Fees (AED)", initial=250)

    def clean_proposal_date(self):
        date = self.cleaned_data['proposal_date']
        if date < datetime.date.today():
            raise forms.ValidationError("Proposal date cannot be in the past")
        return date