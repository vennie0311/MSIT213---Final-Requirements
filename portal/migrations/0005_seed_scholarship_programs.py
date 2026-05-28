from django.db import migrations


def create_scholarship_programs(apps, schema_editor):
    ScholarshipProgram = apps.get_model('portal', 'ScholarshipProgram')
    ScholarshipProgram.objects.bulk_create([
        ScholarshipProgram(
            name='CHED Scholarship',
            provider='CHED',
            description='A government-supported scholarship for eligible college students.',
            region='Region 1',
            active=True,
        ),
        ScholarshipProgram(
            name='DOST Scholarships',
            provider='DOST',
            description='Science and technology scholarships for high-performing students.',
            region='Region 2',
            active=True,
        ),
        ScholarshipProgram(
            name='TES Program',
            provider='TES',
            description='Technical-education support scholarships for regional applicants.',
            region='Region 3',
            active=True,
        ),
    ])


def reverse_scholarship_programs(apps, schema_editor):
    ScholarshipProgram = apps.get_model('portal', 'ScholarshipProgram')
    ScholarshipProgram.objects.filter(name__in=['CHED Scholarship', 'DOST Scholarships', 'TES Program']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_scholarshipprogram'),
    ]

    operations = [
        migrations.RunPython(create_scholarship_programs, reverse_scholarship_programs),
    ]
