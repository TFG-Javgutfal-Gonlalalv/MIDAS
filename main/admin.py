from django.contrib import admin

from main.models import Class, Attribute, Relation, Run, FrequentAttributes, Prepositions, Technicality, UserExtras

admin.site.register(Run)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "score", "run_fk")
    list_filter = ("run_fk",)
    search_fields = ("name",)


@admin.register(Attribute)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "score", "run_fk", "class_fk")
    search_fields = ("name",)
    list_filter = ("run_fk",)


@admin.register(Relation)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("class_fk_1", "verb", "class_fk_2", "run_fk")
    list_filter = ("run_fk",)


@admin.register(FrequentAttributes)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    list_filter = ("name",)


@admin.register(Prepositions)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("name",)


@admin.register(Technicality)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("name",)

@admin.register(UserExtras)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("user_fk","peticiones")
    list_filter = ("user_fk","peticiones")