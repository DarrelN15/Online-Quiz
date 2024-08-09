import random
from django.shortcuts import render, get_object_or_404
from .models import Quiz, Question, Option, QuizAttempt, QuestionResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.core.paginator import Paginator

def home(request):
    return render(request, 'home.html')

# def quizzes(request):
#     quizzes_list = Quiz.objects.all()
#     paginator = Paginator(quizzes_list, 10)  # Show 10 quizzes per page
#     page_number = request.GET.get('page')
#     quizzes = paginator.get_page(page_number)
#     return render(request, 'quizzes.html', {'quizzes': quizzes})

def quizzes_view(request):
    quizzes_list = Quiz.objects.all().order_by('id')
    paginator = Paginator(quizzes_list, 10)  # Show 10 quizzes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'quizzes.html', {'quizzes': page_obj})


def about(request):
    return render(request, 'about.html')

def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    for question in questions:
        options = list(question.options.all())
        random.shuffle(options)
        question.shuffled_options = options

    score = None
    total = len(questions)

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_option_ids = request.POST.getlist(str(question.id))
            selected_options = Option.objects.filter(id__in=selected_option_ids)
            correct_options = question.correct_options.all()
            if set(selected_options) == set(correct_options):
                score += 1

        return render(request, 'quiz_detail.html', {'quiz': quiz, 'questions': questions, 'score': score, 'total': total})

    return render(request, 'quiz_detail.html', {'quiz': quiz, 'questions': questions, 'score': score, 'total': total})

import logging
logger = logging.getLogger(__name__)

@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    score = 0
    total_questions = questions.count()
    
    # Create QuizAttempt instance
    attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, total_questions=total_questions)

    for question in questions:
        selected_option_ids = request.POST.getlist(str(question.id))
        selected_options = Option.objects.filter(id__in=selected_option_ids)
        is_correct = set(selected_options) == set(question.correct_options.all())
        if is_correct:
            score += 1
        
        response = QuestionResponse.objects.create(
            attempt=attempt,
            question=question,
            is_correct=is_correct
        )
        response.selected_options.set(selected_options)

    attempt.score = score
    attempt.save()

    return render(request, 'quiz_result.html', {'quiz': quiz, 'score': score, 'total': total_questions})





def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_success_view(request):
    return redirect('home')

@staff_member_required
def admin_results_view(request):
    if not request.user.is_staff:
        return redirect('home')
    attempts = QuizAttempt.objects.all()
    return render(request, 'admin_results.html', {'attempts': attempts})

def logout_view(request):
    logout(request)
    return redirect('home')