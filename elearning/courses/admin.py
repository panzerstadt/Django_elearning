from django.contrib import admin

from courses.models import Course, Section, Question, Answer

# makes an admin for the app by inheriting from django's default model admin
class CourseAdmin(admin.ModelAdmin):
    pass

class SectionAdmin(admin.ModelAdmin):
    pass

class QuestionAdmin(admin.ModelAdmin):
    pass

class AnswerAdmin(admin.ModelAdmin):
    pass


# then register the database to lock it from random changes, using CourseAdmin as the administrator of this model (db)
admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
