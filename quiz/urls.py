from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('test-logging/', views.test_logging, name='test_logging'),
    path('about/', views.about, name='about'),
    path('quizzes/', views.quizzes_view, name='quizzes'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('quiz/results/', views.quiz_results_view, name='quiz_results'),
]
