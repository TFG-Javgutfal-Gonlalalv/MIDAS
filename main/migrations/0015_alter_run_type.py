# Generated by Django 4.0.6 on 2022-08-31 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_rename_money_userextras_peticiones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='run',
            name='type',
            field=models.CharField(default='NLP', max_length=5),
        ),
    ]
