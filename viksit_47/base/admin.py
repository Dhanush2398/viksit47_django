from django.contrib import admin
from .models import Mock, Question, Option

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4 

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'mock')
    inlines = [OptionInline]

class MockAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'time_limit')

admin.site.register(Mock, MockAdmin)
admin.site.register(Question, QuestionAdmin)
