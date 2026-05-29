from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView as JWTTokenObtainPairView, TokenRefreshView as JWTTokenRefreshView

from .forms import RegistrationForm, CoordinatorCreationForm, ScholarshipApplicationForm, ScholarshipProgramForm, ScholarshipTypeForm
from .models import ApplicantProfile, CoordinatorProfile, ScholarshipProgram, ScholarshipApplication, ScholarshipType
from .serializers import ScholarshipApplicationStatusSerializer


class HomeView(TemplateView):
    template_name = 'portal/home.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff and not request.user.is_superuser:
            return redirect('portal:coordinator_dashboard')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    template_name = 'portal/login.html'

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        if self.request.user.is_staff:
            return reverse_lazy('portal:coordinator_dashboard')
        return reverse_lazy('portal:student_dashboard')


class RegisterView(View):
    template_name = 'portal/register.html'

    def get(self, request):
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            ApplicantProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful. You can now create your scholarship application.')
            return redirect('portal:student_dashboard')
        return render(request, self.template_name, {'form': form})


def is_admin(user):
    return user.is_superuser


def require_admin(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('portal:login')
        if not is_admin(request.user):
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('portal:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


def is_coordinator(user):
    return user.is_staff or user.is_superuser


def require_coordinator(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('portal:login')
        if not is_coordinator(request.user):
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('portal:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


@method_decorator(require_admin, name='dispatch')
class AddCoordinatorView(View):
    template_name = 'portal/add_coordinator.html'

    def get(self, request):
        form = CoordinatorCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CoordinatorCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coordinator account created successfully.')
            return redirect('portal:coordinator_list')
        return render(request, self.template_name, {'form': form})


@method_decorator(require_admin, name='dispatch')
class CoordinatorListView(View):
    template_name = 'portal/coordinator_list.html'

    def get(self, request):
        coordinators = User.objects.filter(is_staff=True).select_related('coordinatorprofile')
        return render(request, self.template_name, {'coordinators': coordinators})


@method_decorator(require_admin, name='dispatch')
class ScholarshipTypeListView(View):
    template_name = 'portal/scholarship_type_list.html'

    def get(self, request):
        types = ScholarshipType.objects.all()
        return render(request, self.template_name, {'types': types})


@method_decorator(require_admin, name='dispatch')
class AddScholarshipTypeView(View):
    template_name = 'portal/add_scholarship_type.html'

    def get(self, request):
        form = ScholarshipTypeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ScholarshipTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Scholarship type created successfully.')
            return redirect('portal:scholarship_type_list')
        return render(request, self.template_name, {'form': form})


@login_required
@require_coordinator
def coordinator_dashboard(request):
    if is_coordinator(request.user) and not request.user.is_superuser:
        return redirect('portal:coordinator_dashboard')

    selected_region = request.GET.get('region')
    available_regions = [region for region, _ in ScholarshipApplication._meta.get_field('region').choices]
    applications = ScholarshipApplication.objects.filter(applicant=request.user)
    if selected_region:
        applications = applications.filter(region__iexact=selected_region)
    return render(request, 'portal/application_list.html', {
        'applications': applications,
        'available_regions': available_regions,
        'selected_region': selected_region,
    })


@login_required
def scholarship_catalog(request):
    selected_region = request.GET.get('region')
    available_regions = [region for region, _ in ScholarshipProgram._meta.get_field('region').choices]
    programs = ScholarshipProgram.objects.filter(active=True)

    if is_coordinator(request.user) and not request.user.is_superuser:
        coordinator_profile = CoordinatorProfile.objects.filter(user=request.user).first()
        if coordinator_profile and coordinator_profile.scholarship_type:
            programs = programs.filter(scholarship_type=coordinator_profile.scholarship_type)
        else:
            programs = ScholarshipProgram.objects.none()

    if selected_region:
        programs = programs.filter(region__iexact=selected_region)
    return render(request, 'portal/scholarship_catalog.html', {
        'programs': programs,
        'available_regions': available_regions,
        'selected_region': selected_region,
    })


@login_required
def student_dashboard(request):
    if is_coordinator(request.user) and not request.user.is_superuser:
        return redirect('portal:coordinator_dashboard')

    selected_region = request.GET.get('region')
    available_regions = [region for region, _ in ScholarshipApplication._meta.get_field('region').choices]
    applications = ScholarshipApplication.objects.filter(applicant=request.user)
    if selected_region:
        applications = applications.filter(region__iexact=selected_region)
    return render(request, 'portal/application_list.html', {
        'applications': applications,
        'available_regions': available_regions,
        'selected_region': selected_region,
    })


@login_required
@require_coordinator
def coordinator_dashboard(request):
    status = request.GET.get('status')
    applications = ScholarshipApplication.objects.all().order_by('-submitted_at')
    coordinator_profile = CoordinatorProfile.objects.filter(user=request.user).first()
    assigned_type = None

    if coordinator_profile and not request.user.is_superuser:
        assigned_type = coordinator_profile.scholarship_type
        selected_type = assigned_type.name if assigned_type else None
        applications = applications.filter(program__scholarship_type=assigned_type)
    else:
        selected_type = request.GET.get('scholarship_type')
        if selected_type:
            applications = applications.filter(program__scholarship_type__name__iexact=selected_type)

    if status:
        applications = applications.filter(status=status)

    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_applications')
        if selected_ids and action in ['approved', 'review', 'rejected']:
            allowed_ids = set(applications.values_list('id', flat=True))
            target_qs = ScholarshipApplication.objects.filter(id__in=selected_ids, pk__in=allowed_ids)
            if action == 'rejected':
                reason = (request.POST.get('rejection_reason') or '').strip()
                if not reason:
                    messages.error(request, 'Please provide a rejection reason when rejecting applications.')
                    return redirect('portal:coordinator_dashboard')
                # Save status and rejection reason per application
                for app in target_qs:
                    prev = app.notes or ''
                    app.status = 'rejected'
                    app.notes = f"Rejected by {request.user.get_full_name() or request.user.username}: {reason}\n\n{prev}"
                    app.save(update_fields=['status', 'notes'])
            else:
                # bulk update for approval/review
                target_qs.update(status=action)
            messages.success(request, 'Selected applications have been updated.')
            return redirect('portal:coordinator_dashboard')

    return render(request, 'portal/coordinator_dashboard.html', {
        'applications': applications,
        'selected_type': assigned_type,
        'selected_status': status,
        'assigned_type': assigned_type,
    })


@login_required
def application_create(request):
    profile = ApplicantProfile.objects.filter(user=request.user).first()
    if not profile:
        messages.error(request, 'Please complete your profile during registration first.')
        return redirect('portal:student_dashboard')
    
    # Coordinators should not submit applications
    if is_coordinator(request.user) and not request.user.is_superuser:
        messages.error(request, 'Coordinators are not allowed to submit scholarship applications.')
        return redirect('portal:coordinator_dashboard')
    
    selected_program = None
    program_id = request.GET.get('program_id') or (request.POST.get('program') if request.method == 'POST' else None)
    
    if program_id:
        # Try to get the program from the ID to display it on the page
        selected_program = ScholarshipProgram.objects.filter(pk=program_id, active=True).first()

    if request.method == 'POST':
        # IMPORTANT: request.FILES is required for your birth certificate, form 137, etc.
        form = ScholarshipApplicationForm(request.POST, request.FILES)
        
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            
            # If the program wasn't in the form, assign the one from the URL/GET
            if not application.program and selected_program:
                application.program = selected_program
                
            application.save()
            
            messages.success(request, 'Application submitted successfully with required documents!')
            return redirect('portal:student_dashboard')
        else:
            # Error handling for the main form (including file errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = ScholarshipApplicationForm(initial={'program': selected_program} if selected_program else None)
    
    return render(request, 'portal/application_form.html', {
        'form': form,
        'selected_program': selected_program,
    })

@login_required
def application_detail(request, pk):
    application = get_object_or_404(ScholarshipApplication, pk=pk)
    if application.applicant == request.user:
        return render(request, 'portal/application_detail.html', {'application': application})

    if is_coordinator(request.user):
        coordinator_profile = CoordinatorProfile.objects.filter(user=request.user).first()
        if request.user.is_superuser or (coordinator_profile and application.program and application.program.scholarship_type == coordinator_profile.scholarship_type):
            return render(request, 'portal/application_detail.html', {'application': application})

    raise Http404('Application not found.')


class TokenObtainPairView(JWTTokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class TokenRefreshView(JWTTokenRefreshView):
    permission_classes = [permissions.AllowAny]


class ApplicationStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        application = get_object_or_404(ScholarshipApplication, pk=pk)
        if request.user.is_authenticated:
            if is_coordinator(request.user) and not request.user.is_superuser:
                coordinator_profile = CoordinatorProfile.objects.filter(user=request.user).first()
                if not (coordinator_profile and application.program and application.program.scholarship_type == coordinator_profile.scholarship_type):
                    return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ScholarshipApplicationStatusSerializer(application)
            return Response(serializer.data)
        return Response({'message': 'Restricted Data'}, status=status.HTTP_401_UNAUTHORIZED)


@login_required
def scholarship_program_detail(request, pk):
    program = get_object_or_404(ScholarshipProgram, pk=pk)
    return render(request, 'portal/program_detail.html', {'program': program})


@method_decorator(require_coordinator, name='dispatch')
class AddScholarshipView(View):
    template_name = 'portal/add_scholarship.html'

    def get(self, request):
        form = ScholarshipProgramForm()
        if not request.user.is_superuser:
            coordinator_profile = CoordinatorProfile.objects.filter(user=request.user).first()
            if coordinator_profile and coordinator_profile.scholarship_type:
                form.fields['scholarship_type'].queryset = ScholarshipType.objects.filter(pk=coordinator_profile.scholarship_type.pk)
                form.fields['scholarship_type'].initial = coordinator_profile.scholarship_type.pk
                form.fields['scholarship_type'].disabled = True
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not request.user.is_superuser:
            coordinator_profile = CoordinatorProfile.objects.filter(user=request.user).first()
            if coordinator_profile and coordinator_profile.scholarship_type:
                data = request.POST.copy()
                data['scholarship_type'] = str(coordinator_profile.scholarship_type.pk)
                form = ScholarshipProgramForm(data)
            else:
                form = ScholarshipProgramForm(request.POST)
        else:
            form = ScholarshipProgramForm(request.POST)

        if form.is_valid():
            program = form.save(commit=False)
            program.created_by = request.user
            program.save()
            messages.success(request, 'Scholarship program created successfully.')
            return redirect('portal:scholarship_catalog')
        return render(request, self.template_name, {'form': form})
    
@method_decorator(require_admin, name='dispatch')
class EditScholarshipTypeView(View):
    template_name = 'portal/edit_scholarship_type.html'

    def get(self, request, pk):
        scholarship_type = get_object_or_404(ScholarshipType, pk=pk)
        form = ScholarshipTypeForm(instance=scholarship_type)
        return render(request, self.template_name, {'form': form, 'scholarship_type': scholarship_type})

    def post(self, request, pk):
        scholarship_type = get_object_or_404(ScholarshipType, pk=pk)
        form = ScholarshipTypeForm(request.POST, instance=scholarship_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Scholarship type updated successfully.')
            return redirect('portal:scholarship_type_list')
        return render(request, self.template_name, {'form': form, 'scholarship_type': scholarship_type})


@method_decorator(require_admin, name='dispatch')
class DeleteScholarshipTypeView(View):
    def post(self, request, pk):
        scholarship_type = get_object_or_404(ScholarshipType, pk=pk)
        scholarship_type.delete()
        messages.success(request, 'Scholarship type deleted successfully.')
        return redirect('portal:scholarship_type_list')
