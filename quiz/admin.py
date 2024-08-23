from django.contrib import admin
from .models import Quiz, Question, Option, QuizAttempt, QuestionResponse

# Inline for displaying QuestionResponse within the QuizAttempt admin
class QuestionResponseInline(admin.TabularInline):
    model = QuestionResponse
    extra = 0
    fields = ('question', 'is_correct', 'selected_options')  # Fields to display
    readonly_fields = ('question', 'is_correct', 'selected_options')  # Make these fields read-only

# Custom admin class for managing QuizAttempt objects
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'date_taken', 'is_completed')  # Fields displayed in the list view
    actions = ['reset_quiz_attempt']  # Custom action to reset quiz attempts
    list_filter = ('quiz', 'user', 'date_taken')  # Filters for narrowing down the list
    search_fields = ('user__username', 'quiz__title')  # Fields to search by
    inlines = [QuestionResponseInline]  # Inline display for question responses
    
    # Custom action to reset the quiz attempt completion status
    def reset_quiz_attempt(self, request, queryset):
        queryset.update(is_completed=False)  # Marks selected quiz attempts as not completed
        self.message_user(request, "Quiz attempts reset for selected users")  # Displays a success message

# Registering the models with the admin site
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
