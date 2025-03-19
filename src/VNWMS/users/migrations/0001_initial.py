# Generated by Django 3.2.25 on 2025-03-19 13:20

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('emp_no', models.CharField(max_length=30, unique=True, verbose_name='emp_no')),
                ('sap_emp_no', models.CharField(blank=True, max_length=30, null=True, verbose_name='sap_emp_no')),
                ('username', models.CharField(max_length=30, verbose_name='username')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email address')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('shot', models.FileField(blank=True, null=True, upload_to='uploads/profile')),
                ('mobile_number', models.CharField(blank=True, help_text='Required. digits and +-() only.', max_length=30, validators=[django.core.validators.RegexValidator('^[0-9+()-]+$', 'Enter a valid mobile number.', 'invalid')], verbose_name='mobile number')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_manager', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'permissions': (('perm_stock', '庫存管理系統權限'),),
            },
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('type_id', models.IntegerField(primary_key=True, serialize=False)),
                ('type_name', models.CharField(max_length=50, verbose_name='類別')),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_at', models.DateTimeField(auto_now=True, null=True)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_type_create_at', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_type_update_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unitId', models.CharField(max_length=30, unique=True, verbose_name='部門編號')),
                ('orgId', models.CharField(max_length=30, verbose_name='組織編號')),
                ('unitName', models.CharField(max_length=30, verbose_name='部門名稱')),
                ('isValid', models.CharField(default=0, max_length=1, verbose_name='失效')),
                ('cost_center', models.CharField(blank=True, max_length=30, null=True, verbose_name='成本中心')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True, null=True)),
                ('create_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='unit_create_by', to=settings.AUTH_USER_MODEL)),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='unit_manager', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='unit_update_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HomePageOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('name_tw', models.CharField(max_length=100)),
                ('name_cn', models.CharField(max_length=100)),
                ('name_vn', models.CharField(max_length=100)),
                ('url_name', models.CharField(max_length=200)),
                ('roles', models.ManyToManyField(blank=True, to='auth.Group')),
            ],
        ),
    ]
