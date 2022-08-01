# Generated by Django 4.0.6 on 2022-07-19 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_attribute_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrequentAttributes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('type', models.CharField(default='varchar(50)', max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Technicality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
    ]