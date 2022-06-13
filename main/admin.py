from django.contrib import admin

from main.models import Class, Attribute, Relation, Run

admin.site.register(Run)
admin.site.register(Class)
admin.site.register(Attribute)
admin.site.register(Relation)
