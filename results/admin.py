from django.contrib import admin
from .models import *

class MathleteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'mao_id', 'school')

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'category')

class TestAdmin(admin.ModelAdmin):
    list_display = ('competition', 'division')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'number', 'answer', 'num_correct', 'num_blank', 'num_wrong')

class TestPaperAdmin(admin.ModelAdmin):
    list_display = ('test', 'place', 'mathlete', 'school')

class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('paper', 'question', 'givenanswer', 'points')

class MathleteImpressionAdmin(admin.ModelAdmin):
    list_display = ('mathlete', 'user', 'datetime')

class UserRequestAdmin(admin.ModelAdmin):
    list_display = ('text', 'datetime')

admin.site.register(Mathlete, MathleteAdmin)
admin.site.register(School)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(TestPaper, TestPaperAdmin)
admin.site.register(QuestionAnswer, QuestionAnswerAdmin)
admin.site.register(Team)
admin.site.register(MathleteImpression, MathleteImpressionAdmin)
admin.site.register(UserRequest, UserRequestAdmin)
