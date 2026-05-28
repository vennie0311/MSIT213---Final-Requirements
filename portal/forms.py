from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import formset_factory

from .models import ApplicantProfile, CoordinatorProfile, ScholarshipApplication, EducationBackground, ScholarshipProgram, ScholarshipType


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=32, required=False)
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_honeypot(self):
        data = self.cleaned_data.get('honeypot')
        if data:
            raise forms.ValidationError('Spam detected.')
        return data


class LoginForm(AuthenticationForm):
    pass


class CoordinatorCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    scholarship_type = forms.ModelChoiceField(
        queryset=ScholarshipType.objects.all(),
        required=True,
        label='Scholarship Type',
        empty_label='Select scholarship type'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'scholarship_type']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = True
        if commit:
            user.save()
            CoordinatorProfile.objects.create(
                user=user,
                scholarship_type=self.cleaned_data['scholarship_type'],
            )
        return user


class ScholarshipApplicationForm(forms.ModelForm):
    program = forms.ModelChoiceField(
        queryset=ScholarshipProgram.objects.filter(active=True),
        required=True,
        label='Scholarship Program',
        empty_label='Select program',
    )

    class Meta:
        model = ScholarshipApplication
        fields = [
            'program',
            'title',
            'identity_document',
            'transcript_document',
            'proof_of_address',
            'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


class ScholarshipProgramForm(forms.ModelForm):
    scholarship_type = forms.ModelChoiceField(
        queryset=ScholarshipType.objects.all(),
        required=False,
        label='Scholarship Type',
        empty_label='Select scholarship type'
    )

    class Meta:
        model = ScholarshipProgram
        fields = ['name', 'description', 'region', 'scholarship_type', 'active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ScholarshipTypeForm(forms.ModelForm):
    class Meta:
        model = ScholarshipType
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class EducationBackgroundForm(forms.ModelForm):
    class Meta:
        model = EducationBackground
        fields = ['institution_name', 'degree', 'year_completed']
    
    def clean(self):
        cleaned_data = super().clean()
        institution = cleaned_data.get('institution_name')
        degree = cleaned_data.get('degree')
        year = cleaned_data.get('year_completed')
        
        # Allow all fields to be empty (for extra forms), but require all or none
        has_institution = bool(institution)
        has_degree = bool(degree)
        has_year = bool(year)
        
        if (has_institution or has_degree or has_year):
            if not (has_institution and has_degree and has_year):
                raise forms.ValidationError('All education fields must be filled if any is provided.')
        
        return cleaned_data


EducationBackgroundFormSet = formset_factory(EducationBackgroundForm, extra=1, min_num=1, validate_min=True, validate_max=False)
