from django.http import HttpResponse
import random
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Quiz, Question, Option, QuizAttempt, QuestionResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import EditProfileForm, CustomPasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.dateparse import parse_date
import logging

logger = logging.getLogger(__name__)

def test_logging(request):
    logger.debug("Test logging view called")
    return HttpResponse("Logging test successful")

#1 Creating homepage 
def home(request):
    return render(request, 'home.html')

#2 Creating quiz view
def quizzes_view(request):
    logger.debug("Quiz view called")
    quizzes_list = Quiz.objects.all().order_by('id')
    paginator = Paginator(quizzes_list, 10)  # Show 10 quizzes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'quizzes.html', {'quizzes': page_obj})



def about(request):
    logger.debug(f"About view called")
    return render(request, 'about.html')

def quiz_detail(request, quiz_id):
    logger.debug(f"Quiz Detail view called")
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


@login_required
def submit_quiz(request, quiz_id):
    logger.debug(f"Submit Quiz view called for quiz_id: {quiz_id}")

    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all()
        score = 0
        total_questions = questions.count()

        logger.debug(f"Quiz retrieved: {quiz.title} with {total_questions} questions")

        try:
            attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, score=0)
            logger.info(f"QuizAttempt created for user: {request.user} and quiz: {quiz.title}")
        except Exception as e:
            logger.error(f"Error creating QuizAttempt for user: {request.user} and quiz: {quiz.title}: {e}")
            return render(request, 'error_page.html', {'message': 'Error saving quiz attempt. Please try again.'})

        for question in questions:
            selected_option_ids = request.POST.getlist(str(question.id))
            selected_options = Option.objects.filter(id__in=selected_option_ids)
            is_correct = set(selected_options) == set(question.correct_options.all())
            if is_correct:
                score += 1
            
            logger.debug(f"Question {question.id} answered. Correct: {is_correct}, Selected options: {[option.id for option in selected_options]}")

            try:
                response = QuestionResponse.objects.create(attempt=attempt, question=question, is_correct=is_correct)
                response.selected_options.set(selected_options)
                logger.info(f"QuestionResponse saved for question: {question.id}, is_correct: {is_correct}")
            except Exception as e:
                logger.error(f"Error saving QuestionResponse for question: {question.id} in quiz attempt: {attempt.id}: {e}")

        logger.info(f'User {request.user} submitted quiz {quiz_id} with score {score} out of {total_questions}')

        # Update the attempt with the final score
        attempt.score = score
        try:
            attempt.save()
            logger.info(f"QuizAttempt updated with final score: {score} for user: {request.user}")
        except Exception as e:
            logger.error(f"Error updating QuizAttempt with final score: {e}")

        # Render the results on the same page
        return render(request, 'quiz_detail.html', {
            'quiz': quiz,
            'score': score,
            'total': total_questions,
            'questions': questions
        })

    return redirect('quiz_detail', quiz_id=quiz_id)


def register(request):
    logger.debug(f"Register view called")
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_success_view(request):
    logger.debug(f"Login view called")
    return redirect('home')

from django.db.models import Q

@staff_member_required
def quiz_results_view(request):
    logger.debug("Quiz results view called")
    if not request.user.is_staff:
        return redirect('home')
    
    # Get filters from the request
    user_filter = request.GET.get('user')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    score_min = request.GET.get('score_min')
    score_max = request.GET.get('score_max')
    quiz_filter = request.GET.get('quiz')
    sort_by = request.GET.get('sort_by', 'date_taken')

    # Initial filter based on specific fields
    attempts = QuizAttempt.objects.all()

    if user_filter:
        attempts = attempts.filter(user__username__icontains=user_filter)
    
    if quiz_filter:
        attempts = attempts.filter(quiz__title__icontains=quiz_filter)
    
    if date_from:
        attempts = attempts.filter(date_taken__gte=parse_date(date_from))
    
    if date_to:
        attempts = attempts.filter(date_taken__lte=parse_date(date_to))
    
    if score_min:
        attempts = attempts.filter(score__gte=int(score_min))
    
    if score_max:
        attempts = attempts.filter(score__lte=int(score_max))
    
    # Implement the search functionality here
    search_query = request.GET.get('search')
    if search_query:
        attempts = attempts.filter(
            Q(user__username__icontains=search_query) |
            Q(quiz__title__icontains=search_query) |
            Q(date_taken__icontains=search_query)
        )

    logger.debug(f"Found {attempts.count()} quiz attempts after filtering.")
    
    # Process attempts for percentage and sorting
    attempt_data = []
    for attempt in attempts:
        total_questions = attempt.quiz.questions.count()
        correct_answers = attempt.score
        percentage_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Determine badge color based on percentage score
        if percentage_score >= 80:
            badge_color = "bg-success"
        elif 50 <= percentage_score < 80:
            badge_color = "bg-warning"
        else:
            badge_color = "bg-danger"
        
        attempt_data.append({
            'attempt': attempt,
            'total_questions': total_questions,
            'percentage_score': percentage_score,
            'badge_color': badge_color,
        })
        
    # Sort the attempt data based on the selected sorting option
    if sort_by == 'percentage':
        attempt_data.sort(key=lambda x: x['percentage_score'], reverse=True)
    elif sort_by == 'score':
        attempt_data.sort(key=lambda x: x['attempt'].score, reverse=True)
    elif sort_by == 'user':
        attempt_data.sort(key=lambda x: x['attempt'].user.username.lower())
    elif sort_by == 'quiz_title':
        attempt_data.sort(key=lambda x: x['attempt'].quiz.title.lower())
    else:  # default sorting by date_taken
        attempt_data.sort(key=lambda x: x['attempt'].date_taken, reverse=True)
    
    paginator = Paginator(attempt_data, 10)  # Show 10 attempts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'quiz_results.html', {
        'page_obj': page_obj,
        'sort_by': sort_by,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'score_min': score_min,
        'score_max': score_max,
        'quiz_filter': quiz_filter,
        'search_query': search_query,  # Pass the search query back to the template
    })


@login_required
def quiz_attempt_detail(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    questions = attempt.quiz.questions.all()

    # Prepare a list of dictionaries to pass to the template
    question_data = []
    total_questions = questions.count()
    correct_answers = 0

    for question in questions:
        question_response = QuestionResponse.objects.get(attempt=attempt, question=question)
        selected_options = question_response.selected_options.all()
        is_correct = set(selected_options) == set(question.correct_options.all())
        
        if is_correct:
            correct_answers += 1
        
        question_data.append({
            'question': question,
            'correct_options': question.correct_options.all(),
            'selected_options': selected_options,
        })

    # Calculate percentage score
    percentage_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    context = {
        'attempt': attempt,
        'question_data': question_data,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'percentage_score': percentage_score,
    }
    return render(request, 'quiz_attempt_detail.html', context)

def logout_view(request):
    logger.debug(f"Logout view called")
    logout(request)
    return redirect('home')

# @login_required
# def profile_view(request):
#     is_admin = request.user.is_staff
#     password_form = PasswordChangeForm(request.user)
#     return render(request, 'profile.html', {'password_form': password_form})

@login_required
def profile_view(request):
    is_admin = request.user.is_staff  # Check if the user is an admin
    return render(request, 'profile.html', {'is_admin': is_admin})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('edit_profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important, to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})