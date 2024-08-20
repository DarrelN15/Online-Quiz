from django.contrib import admin
from .models import Quiz, Question, Option, QuizAttempt, QuestionResponse

class QuestionResponseInline(admin.TabularInline):
    model = QuestionResponse
    extra = 0
    fields = ('question', 'is_correct', 'selected_options')
    readonly_fields = ('question', 'is_correct', 'selected_options')

class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'date_taken', 'is_completed')
    actions = ['reset_quiz_attempt']
    list_filter = ('quiz', 'user', 'date_taken')
    search_fields = ('user__username', 'quiz__title')
    inlines = [QuestionResponseInline]
    
    def reset_quiz_attempt(self, request, queryset):
        queryset.update(is_completed=False)
        self.message_user(request, "Quiz attempts reset for selected users")

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
