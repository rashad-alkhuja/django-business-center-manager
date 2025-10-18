# offices/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import View
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from weasyprint import HTML
import os
from django.conf import settings
from pathlib import Path
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test

# --- The models are imported from the correct app's models.py ---
from .models import Office
from .serializers import OfficeSerializer
from .forms import ProposalForm
from django.views.generic import TemplateView

# This helper function is used by the decorators below
def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Manager').exists()

# --- VIEWS FOR THE OFFICES APP ---

class FloorPlanView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Manager').exists()
    def handle_no_permission(self):
        return redirect('dashboard')
    def get(self, request, *args, **kwargs):
        all_offices = Office.objects.all().order_by('office_number')
        context = {'offices': all_offices}
        return render(request, 'offices/index.html', context)

@login_required(login_url='/login/')
@user_passes_test(is_manager, login_url='/dashboard/')
def create_proposal_view(request, office_number):
    office = get_object_or_404(Office, pk=office_number)
    form = ProposalForm(initial={'annual_rent': office.annual_rent})
    context = {'form': form, 'office': office}
    return render(request, 'offices/create_proposal.html', context)

@login_required(login_url='/login/')
@user_passes_test(is_manager, login_url='/dashboard/')
def generate_pdf_view(request, office_number):
    office = get_object_or_404(Office, pk=office_number)
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal_data = form.cleaned_data
            logo_path_obj = Path(settings.STATICFILES_DIRS[0]) / 'offices/images/Rahet-Logo.png'
            logo_uri = logo_path_obj.as_uri()
            context = {
                'office': office, 'proposal': proposal_data,
                'proposal_date': '01/09/2025', 'logo_path': logo_uri,
            }
            html_string = render_to_string('offices/proposal_pdf_template.html', context)
            pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Lease-Proposal-Office-{office.office_number}.pdf"'
            return response
    return create_proposal_view(request, office_number)

class OfficeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Office.objects.all().order_by('office_number')
    serializer_class = OfficeSerializer

@api_view(['GET'])
def office_statistics_view(request):
    try:
        available_count = Office.objects.filter(status='available').count()
        rented_count = Office.objects.filter(status='rented').count()
        data = {'available_count': available_count, 'rented_count': rented_count}
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@login_required(login_url='/login/')
@user_passes_test(is_manager, login_url='/dashboard/')
def statistics_view(request):
    return render(request, 'offices/statistics.html')