# Generated by Django 4.0.6 on 2022-08-09 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_class_deleted_run_type_userextras_money'),
    ]

    operations = [
        migrations.AddField(
            model_name='run',
            name='correcion_manual',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='run',
            name='run_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='run_modificada', to='main.run'),
        ),
    ]