from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page showing list of quizzes
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),  # Quiz detail page
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),  # Quiz result page
]
