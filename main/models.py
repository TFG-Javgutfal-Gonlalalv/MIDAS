from django.db import models
from django.contrib.auth.models import User


class UserExtras(models.Model):
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE, null=False)


class Run(models.Model):
    text = models.TextField(null=False, default="",
                            help_text="Este será el texto del que se extraerán las entidades para el modelado")
    run_datetime = models.DateTimeField(null=False, auto_now_add=True)
    log_run = models.TextField(default="")
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE, null=False)


class Class(models.Model):
    name = models.CharField(max_length=30)
    score = models.FloatField(null=False, default=1.0)
    run_fk = models.ForeignKey(Run, on_delete=models.CASCADE, null=False)


class Attribute(models.Model):
    name = models.CharField(max_length=50)
    score = models.FloatField(null=False, default=1.0)
    type = models.CharField(max_length=50, default="varchar(255)")
    class_fk = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    run_fk = models.ForeignKey(Run, on_delete=models.CASCADE, null=False)


class Relation(models.Model):
    class_fk_1 = models.ForeignKey(Class, on_delete=models.CASCADE, null=False, related_name="Clase1")
    multiplicity_1 = models.CharField(max_length=1)
    class_fk_2 = models.ForeignKey(Class, on_delete=models.CASCADE, null=False, related_name="Clase2")
    multiplicity_2 = models.CharField(max_length=1)
    verb = models.CharField(max_length=100)
    phrase = models.CharField(max_length=500)
    score = models.FloatField(null=False, default=1.0)
    run_fk = models.ForeignKey(Run, on_delete=models.CASCADE, null=False)


class Technicality(models.Model):
    name = models.CharField(max_length=50)


class FrequentAttributes(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=40, default="varchar(50)")
