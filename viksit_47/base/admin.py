from django.contrib import admin
from .models import Mock, Question, Option, InfoCard

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


@admin.register(InfoCard)
class InfoCardAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "image_preview")
    search_fields = ("title", "description")

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="width:80px; height:80px; object-fit:cover;" />'
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"
