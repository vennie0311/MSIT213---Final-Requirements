from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from .models import ApplicantProfile, CoordinatorProfile, ScholarshipApplication, EducationBackground, ScholarshipProgram, ScholarshipType


class EducationBackgroundInline(admin.TabularInline):
    model = EducationBackground
    extra = 1


class CoordinatorProfileInline(admin.StackedInline):
    model = CoordinatorProfile
    can_delete = False
    verbose_name_plural = 'Coordinator profile'
    fk_name = 'user'


class UserAdmin(DjangoUserAdmin):
    inlines = (CoordinatorProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'applicant', 'get_program_name', 'region', 'status', 'submitted_at')
    list_filter = ('region', 'status', 'program__scholarship_type')
    search_fields = ('title', 'applicant__email', 'applicant__username')
    inlines = [EducationBackgroundInline]

    def get_program_name(self, obj):
        return obj.program.name if obj.program else '-'
    get_program_name.short_description = 'Program'


@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__email', 'user__username')


@admin.register(CoordinatorProfile)
class CoordinatorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'scholarship_type')
    list_filter = ('scholarship_type',)
    search_fields = ('user__email', 'user__username')


@admin.register(ScholarshipProgram)
class ScholarshipProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'scholarship_type', 'active', 'created_at')
    list_filter = ('region', 'scholarship_type', 'active')
    search_fields = ('name',)


@admin.register(ScholarshipType)
class ScholarshipTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
