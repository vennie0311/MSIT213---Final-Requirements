import os
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import ApplicantProfile, CoordinatorProfile, ScholarshipApplication, ScholarshipProgram, ScholarshipType


ALLOWED_EXTENSIONS = [
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
    # Documents
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # Others
    '.txt', '.csv',
]

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise forms.ValidationError(
            f'Unsupported file type "{ext}". Allowed types: images (JPG, PNG, etc.), documents (PDF, DOC, DOCX, XLS, PPT), and text files.'
        )


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
    birth_certificate = forms.FileField(validators=[validate_file_extension])
    form_138 = forms.FileField(validators=[validate_file_extension])
    proof_of_income = forms.FileField(validators=[validate_file_extension])
    other_requirements = forms.FileField(required=False, validators=[validate_file_extension])
    certificate_of_guardianship = forms.FileField(required=False, validators=[validate_file_extension])

    class Meta:
        model = ScholarshipApplication
        fields = [
            'program',
            'birth_certificate',
            'form_138',
            'proof_of_income',
            'other_requirements',
            'certificate_of_guardianship',
        ]


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