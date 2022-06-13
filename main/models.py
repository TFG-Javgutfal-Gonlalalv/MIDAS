from django.db import models


class Run(models.Model):
    text = models.TextField(null=False, default="", help_text="Este será el texto del que se extraerán las entidades para el modelado")
    run_datetime = models.DateTimeField(null=False, auto_now_add=True)
    log_run = models.TextField(default="")


class Class(models.Model):
    name = models.CharField(max_length=30)
    score = models.FloatField(null=False, default=1.0)
    run_fk = models.ForeignKey(Run, on_delete=models.CASCADE, null=False)


class Attribute(models.Model):
    name = models.CharField(max_length=50)
    score = models.FloatField(null=False, default=1.0)
    class_fk = models.ForeignKey(Class, on_delete=models.CASCADE, null=False)


class Relation(models.Model):
    class_fk_1 = models.ForeignKey(Class, on_delete=models.CASCADE, null=False, related_name="Clase1")
    class_fk_2 = models.ForeignKey(Class, on_delete=models.CASCADE, null=False, related_name="Clase2")
    score = models.FloatField(null=False, default=1.0)
