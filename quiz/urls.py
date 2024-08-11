from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('quizzes/', views.quizzes_view, name='quizzes'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('submit_quiz/<int:quiz_id>/', views.submit_quiz, name='submit_quiz'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/results/', views.admin_results_view, name='admin_results'),
]
