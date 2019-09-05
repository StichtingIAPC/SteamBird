from django.contrib import admin

from steambird.models import Book, Course, CourseStudy, MSP, MSPLine, \
    OtherMaterial, ScientificArticle, Study, StudyAssociation, StudyMaterial, \
    StudyMaterialEdition, Teacher, Config, AuthToken

admin.site.register(Study)
admin.site.register(StudyMaterial)
admin.site.register(StudyMaterialEdition)
admin.site.register(Course)
admin.site.register(CourseStudy)
admin.site.register(StudyAssociation)
admin.site.register(Teacher)
admin.site.register(MSP)
admin.site.register(MSPLine)
admin.site.register(Book)
admin.site.register(OtherMaterial)
admin.site.register(ScientificArticle)
admin.site.register(Config)


@admin.register(AuthToken)
class AUthTokenAdmin(admin.ModelAdmin):
    fields = ('user', 'token', 'last_host')
    list_display = (
        'token',
        'user',
        'login_url'
    )

