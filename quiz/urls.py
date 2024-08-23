from django.urls import path
from . import views
from.views import edit_profile, change_password, export_quiz_results_csv

urlpatterns = [
    path('', views.home, name='home'),
    path('test-logging/', views.test_logging, name='test_logging'),
    path('about/', views.about, name='about'),
    path('quizzes/', views.quizzes_view, name='quizzes'),
    path('quiz/attempt/<int:attempt_id>/', views.quiz_attempt_detail, name='quiz_attempt_detail'),  # Detail view for quiz attempts
    path('quiz/attempt/<int:attempt_id>/reset/', views.reset_quiz_attempt, name='reset_quiz_attempt'),
    path('export-quiz-results/', export_quiz_results_csv, name='export_quiz_results_csv'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),  # Detail view for quizzes
    path('quiz/<int:quiz_id>/submit', views.submit_quiz, name='submit_quiz'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('quiz/results/', views.quiz_results_view, name='quiz_results'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('change-password/', change_password, name='change_password'),
    path('quiz/results/reset/', views.reset_filters, name='reset_filters'),
]
