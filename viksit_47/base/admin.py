from django.contrib import admin
from django.contrib.auth.models import User
from .models import Mock, Question, Option, Author, StudyMaterial, StudyMaterialItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'mock')
    inlines = [OptionInline]


class MockAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'difficulty', 'time_limit')
    list_filter = ('course', 'difficulty')
    search_fields = ('title',)

admin.site.register(Mock, MockAdmin)
admin.site.register(Question, QuestionAdmin)



class StudyMaterialItemInline(admin.TabularInline): 
    model = StudyMaterialItem
    extra = 1


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    list_filter = ("course",)
    search_fields = ("title",)
    inlines = [StudyMaterialItemInline]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'education', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="80" height="80" style="object-fit: cover;"/>'
        return "-"
    image_preview.allow_tags = True
    image_preview.short_description = 'Image Preview'

