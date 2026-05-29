from django.conf import settings
from django.db import models

REGION_CHOICES = [
    ('Region 1', 'Region 1'),
    ('Region 2', 'Region 2'),
    ('Region 3', 'Region 3'),
    ('Region 4', 'Region 4'),
    ('Region 5', 'Region 5'),
    ('Region 6', 'Region 6'),
    ('Region 7', 'Region 7'),
    ('Region 8', 'Region 8'),
]


class ScholarshipType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ApplicantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class CoordinatorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scholarship_type = models.ForeignKey(ScholarshipType, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.user and not self.user.is_staff:
            self.user.is_staff = True
            self.user.save(update_fields=['is_staff'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.scholarship_type})'


class ScholarshipProgram(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    region = models.CharField(max_length=128, choices=REGION_CHOICES)
    scholarship_type = models.ForeignKey(ScholarshipType, on_delete=models.SET_NULL, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_programs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.region})'


class ScholarshipApplication(models.Model):
    STATUS_NEW = 'new'
    STATUS_REVIEW = 'review'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_REVIEW, 'In review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    program = models.ForeignKey('ScholarshipProgram', null=True, blank=True, on_delete=models.SET_NULL, related_name='applications')
    region = models.CharField(max_length=128, choices=REGION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    submitted_at = models.DateTimeField(auto_now_add=True)
    birth_certificate = models.FileField(upload_to='documents/')
    form_138 = models.FileField(upload_to='documents/')
    proof_of_income = models.FileField(upload_to='documents/')
    other_requirements = models.FileField(upload_to='documents/', blank=True, null=True)
    certificate_of_guardianship = models.FileField(upload_to='documents/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.program:
            self.region = self.program.region
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.program} - {self.get_status_display()}'
    
