# Generated by Django 5.1.2 on 2024-12-09 22:24

import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
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
                ('instructors', models.ManyToManyField(related_name='courses', to='TAScheduler.instructor')),
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
            name='TA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grader_status', models.BooleanField(default=False)),
                ('skills', models.TextField(blank=True, default='No skills listed', null=True)),
                ('max_assignments', models.IntegerField(default=6, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)])),
                ('sections', models.ManyToManyField(related_name='tas', to='TAScheduler.section')),
            ],
        ),
        migrations.AddField(
            model_name='section',
            name='assigned_tas',
            field=models.ManyToManyField(related_name='assigned_sections', to='TAScheduler.ta'),
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
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('email', models.EmailField(max_length=90, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('home_address', models.CharField(blank=True, max_length=90)),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('is_temporary_password', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_instructor', models.BooleanField(default=False)),
                ('is_ta', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='ta',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ta_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_notifications', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='instructor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='instructor_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Administrator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='administrator_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
