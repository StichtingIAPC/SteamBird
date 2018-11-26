from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from .models import StudyMaterialEdition, Book, ScientificArticle, \
    OtherMaterial, Course, Study, StudyCourse, Teacher, Module, StudyMaterial

admin.site.register(Course)
admin.site.register(Study)
admin.site.register(StudyCourse)
admin.site.register(Teacher)
admin.site.register(Module)
admin.site.register(StudyMaterial)


class StudyMaterialChildAdmin(PolymorphicChildModelAdmin):
    base_model = StudyMaterialEdition
    base_fieldsets = (None, {
        'fields': ('name',)
    })


@admin.register(Book)
class BookAdmin(StudyMaterialChildAdmin):
    base_model = Book
    show_in_index = True
    fields = ('name', 'ISBN', 'author', 'img', 'year_of_publishing')


@admin.register(ScientificArticle)
class ScientificArticleAdmin(StudyMaterialChildAdmin):
    base_model = ScientificArticle
    show_in_index = True
    fields = ('name', 'DOI', 'author', 'year_of_publishing')


@admin.register(OtherMaterial)
class OtherMaterialAdmin(StudyMaterialChildAdmin):
    base_model = OtherMaterial
    show_in_index = True
    fields = ('name', )


@admin.register(StudyMaterialEdition)
class StudyMaterialParentAdmin(PolymorphicParentModelAdmin):
    base_model = StudyMaterialEdition
    child_models = (Book, ScientificArticle, OtherMaterial)
    list_filter = (PolymorphicChildModelFilter, )
