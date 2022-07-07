# Generated by Django 4.0.3 on 2022-06-13 22:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('score', models.FloatField(default=1.0)),
            ],
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(default='', help_text='Este será el texto del que se extraerán las entidades para el modelado')),
                ('run_datetime', models.DateTimeField(auto_now_add=True)),
                ('log_run', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(default=1.0)),
                ('class_fk_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Clase1', to='main.class')),
                ('class_fk_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Clase2', to='main.class')),
            ],
        ),
        migrations.AddField(
            model_name='class',
            name='run_fk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.run'),
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('score', models.FloatField(default=1.0)),
                ('class_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.class')),
            ],
        ),
    ]