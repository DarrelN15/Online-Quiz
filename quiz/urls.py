from django.urls import path
from . import views
from .views import edit_profile, change_password, export_quiz_results_csv

# URL patterns for the application
urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('test-logging/', views.test_logging, name='test_logging'),  # Test logging view
    path('about/', views.about, name='about'),  # About page
    path('quizzes/', views.quizzes_view, name='quizzes'),  # List of available quizzes
    path('quiz/attempt/<int:attempt_id>/', views.quiz_attempt_detail, name='quiz_attempt_detail'),  # Detail view for specific quiz attempts
    path('quiz/attempt/<int:attempt_id>/reset/', views.reset_quiz_attempt, name='reset_quiz_attempt'),  # Reset a specific quiz attempt
    path('export-quiz-results/', export_quiz_results_csv, name='export_quiz_results_csv'),  # Export quiz results as CSV
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),  # Detail view for a specific quiz
    path('quiz/<int:quiz_id>/submit', views.submit_quiz, name='submit_quiz'),  # Submit answers for a specific quiz
    path('register/', views.register, name='register'),  # User registration page
    path('logout/', views.logout_view, name='logout'),  # User logout view
    path('quiz/results/', views.quiz_results_view, name='quiz_results'),  # View quiz results
    path('profile/', views.profile_view, name='profile'),  # User profile page
    path('edit-profile/', edit_profile, name='edit_profile'),  # Edit profile page
    path('change-password/', change_password, name='change_password'),  # Change password page
    path('quiz/results/reset/', views.reset_filters, name='reset_filters'),  # Reset filters for quiz results
]
