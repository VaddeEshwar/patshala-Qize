from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Subject, Question, Option, Explanation

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4
    fields = ('text_content', 'image_content', 'is_correct')
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "is_correct":
            kwargs['help_text'] = "Select only ONE correct option"
        return super().formfield_for_choice_field(db_field, request, **kwargs)

class ExplanationInline(admin.StackedInline):
    model = Explanation
    fields = ('text_content', 'image_content')
    extra = 1
    max_num = 1

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','logo_image')
    search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'question_type', 'preview')
    list_filter = ('subject', 'question_type')
    inlines = [OptionInline, ExplanationInline]
    fields = ('subject', 'question_type', 'text_content', 'image_content', 'hint')
    
    def preview(self, obj):
        if obj.question_type == 'text':
            return obj.text_content[:50] + '...' if obj.text_content else 'No content'
        return "Image Question"
    
    class Media:
        css = {
            'all': ('quiz/css/admin.css',)
        }
        js = ('quiz/js/admin.js',)
