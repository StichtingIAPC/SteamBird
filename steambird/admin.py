from django.conf import settings
from django.contrib import admin
from django.contrib.admin import forms, widgets
from django.forms import Textarea
from polymorphic.admin import PolymorphicParentModelAdmin, \
    PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from django.db import models

from .models import StudyMaterialEdition, Book, ScientificArticle, \
    OtherMaterial, Course, Study, StudyCourse, Teacher, Module, StudyMaterial, \
    MaterialSelectionProcess

admin.site.register(StudyCourse)


@admin.register(MaterialSelectionProcess)
class MaterialSelectionProcessAdmin(admin.ModelAdmin):
    search_fields = ('osiris_specified_material__name',
                     'approved_material__name')
    list_display = ('current_active_book', 'stage')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    search_fields = ('titles', 'initials', 'first_name', 'surname_prefix',
                     'last_name', 'email')
    list_display = ('__str__', 'email', 'last_login')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_code', 'module_moment')
    list_filter = ('module_moment', 'course')
    autocomplete_fields = ('coordinator',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'course_code')
    list_filter = ('study',)
    autocomplete_fields = ('teachers', 'materials')


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'study_type')
    list_filter = ('study_type',)


class StudyMaterialChildAdmin(PolymorphicChildModelAdmin):
    base_model = StudyMaterialEdition
    base_fieldsets = (None, {
        '': ('name', 'material_type')
    })
    fields = ('name', 'material_type')
    autocomplete_fields = ('material_type',)


@admin.register(Book)
class BookAdmin(StudyMaterialChildAdmin):
    base_model = Book
    show_in_index = True
    fields = StudyMaterialChildAdmin.fields + \
             ('ISBN', 'author', 'img', 'year_of_publishing', 'edition')
    list_display = ('name', 'ISBN', 'author', 'year_of_publishing', 'edition')
    list_filter = ('material_type', 'year_of_publishing')


@admin.register(ScientificArticle)
class ScientificArticleAdmin(StudyMaterialChildAdmin):
    base_model = ScientificArticle
    show_in_index = True
    fields = ('name', 'material_type', 'DOI', 'author', 'year_of_publishing')
    list_display = ('name', 'DOI', 'author', 'year_of_publishing')
    list_filter = ('material_type', 'year_of_publishing')


@admin.register(OtherMaterial)
class OtherMaterialAdmin(StudyMaterialChildAdmin):
    base_model = OtherMaterial
    show_in_index = True
    fields = ('name', 'material_type')
    list_display = ('name',)
    list_filter = ('material_type',)


@admin.register(StudyMaterialEdition)
class StudyMaterialParentAdmin(PolymorphicParentModelAdmin):
    base_model = StudyMaterialEdition
    child_models = (Book, ScientificArticle, OtherMaterial)
    list_filter = (PolymorphicChildModelFilter, 'material_type')
