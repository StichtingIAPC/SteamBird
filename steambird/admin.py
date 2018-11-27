from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from .models import StudyMaterialEdition, Book, ScientificArticle, \
    OtherMaterial, Course, Study, StudyCourse, Teacher, Module, StudyMaterial

admin.site.register(StudyCourse)
admin.site.register(Teacher)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_code', 'module_moment')
    list_filter = ('module_moment', 'course__name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'course_code')
    list_filter = ('study__name',)


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'study_type')
    list_filter = ('study_type',)


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
    list_display = ('name', 'ISBN', 'author', 'year_of_publishing')
    list_filter = ('material_type__id', 'year_of_publishing')


@admin.register(ScientificArticle)
class ScientificArticleAdmin(StudyMaterialChildAdmin):
    base_model = ScientificArticle
    show_in_index = True
    fields = ('name', 'DOI', 'author', 'year_of_publishing')
    list_display = ('name', 'DOI', 'author', 'year_of_publishing')
    list_filter = ('material_type__id', 'year_of_publishing')


@admin.register(OtherMaterial)
class OtherMaterialAdmin(StudyMaterialChildAdmin):
    base_model = OtherMaterial
    show_in_index = True
    fields = ('name',)
    list_display = ('name',)
    list_filter = ('material_type__id',)


@admin.register(StudyMaterialEdition)
class StudyMaterialParentAdmin(PolymorphicParentModelAdmin):
    base_model = StudyMaterialEdition
    child_models = (Book, ScientificArticle, OtherMaterial)
    list_filter = (PolymorphicChildModelFilter,)
