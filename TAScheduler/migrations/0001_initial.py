# Generated by Django 5.1.2 on 2024-11-23 15:54

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.CharField(max_length=20, unique=True)),
                ('semester', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('num_of_sections', models.IntegerField()),
                ('modality', models.CharField(choices=[('Online', 'Online'), ('In-person', 'In-person')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_assignments', models.IntegerField(default=6, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='TA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grader_status', models.BooleanField()),
                ('skills', models.TextField(default='No skills listed', null=True)),
                ('max_assignments', models.IntegerField(default=6, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('email_address', models.EmailField(max_length=90, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('home_address', models.CharField(blank=True, max_length=90)),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_instructor', models.BooleanField(default=False)),
                ('is_ta', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='InstructorToCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instructor_assignments', to='TAScheduler.course')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_assignments', to='TAScheduler.instructor')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_id', models.IntegerField()),
                ('location', models.CharField(max_length=30)),
                ('meeting_time', models.TextField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='TAScheduler.course')),
            ],
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instructor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_lectures', to='TAScheduler.instructor')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lectures', to='TAScheduler.section')),
                ('ta', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grading_lectures', to='TAScheduler.ta')),
            ],
        ),
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labs', to='TAScheduler.section')),
                ('ta', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_labs', to='TAScheduler.ta')),
            ],
        ),
        migrations.CreateModel(
            name='TAToCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ta_assignments', to='TAScheduler.course')),
                ('ta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_assignments', to='TAScheduler.ta')),
            ],
        ),
        migrations.AddField(
            model_name='ta',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ta_profile', to='TAScheduler.user'),
        ),
        migrations.CreateModel(
            name='Supervisor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='supervisor_profile', to='TAScheduler.user')),
            ],
        ),
        migrations.AddField(
            model_name='instructor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='instructor_profile', to='TAScheduler.user'),
        ),
        migrations.CreateModel(
            name='Administrator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='administrator_profile', to='TAScheduler.user')),
            ],
        ),
    ]