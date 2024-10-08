import csv
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
from .forms import CustomUserCreationForm
from django.db.models import Q
from django.utils.dateparse import parse_date
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Test logging functionality
def test_logging(request):
    logger.debug("Test logging view called")
    return HttpResponse("Logging test successful")

# Home page view
def home(request):
    return render(request, 'home.html')

# View to display list of quizzes, requires login
@login_required
def quizzes_view(request):
    logger.debug("Quiz view called")
    quizzes_list = Quiz.objects.all().order_by('id')  # Fetch all quizzes ordered by ID
    paginator = Paginator(quizzes_list, 10)  # Show 10 quizzes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'quizzes.html', {'quizzes': page_obj})

# About page view
def about(request):
    logger.debug(f"About view called")
    return render(request, 'about.html')

# View for quiz detail and taking the quiz, requires login
@login_required
def quiz_detail(request, quiz_id):
    logger.debug("Quiz Detail view called")
    quiz = get_object_or_404(Quiz, id=quiz_id)  # Fetch the quiz or return 404 if not found
    questions = quiz.questions.all()

    # Check if the user has already completed this quiz
    try:
        quiz_attempt = QuizAttempt.objects.get(user=request.user, quiz=quiz, is_completed=True)
        score = quiz_attempt.score
        incorrect_answers = len(questions) - score
        return render(request, 'quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total': len(questions),
            'incorrect_answers': incorrect_answers  # Pass incorrect answers
        })
    except QuizAttempt.DoesNotExist:
        # Allow the user to take the quiz
        for question in questions:
            options = list(question.options.all())
            random.shuffle(options)  # Shuffle options to randomize their order
            question.shuffled_options = options

        if request.method == 'POST':
            score = 0
            for question in questions:
                selected_option_ids = request.POST.getlist(str(question.id))
                selected_options = Option.objects.filter(id__in=selected_option_ids)
                correct_options = question.correct_options.all()
                if set(selected_options) == set(correct_options):
                    score += 1

            # Calculate incorrect answers
            incorrect_answers = len(questions) - score

            # Save the quiz attempt
            QuizAttempt.objects.create(user=request.user, quiz=quiz, score=score, is_completed=True)

            return render(request, 'quiz_result.html', {
                'quiz': quiz,
                'score': score,
                'total': len(questions),
                'incorrect_answers': incorrect_answers  # Pass incorrect answers
            })

        return render(request, 'quiz_detail.html', {
            'quiz': quiz,
            'questions': questions
        })

# View to handle quiz submission, requires login
@login_required
def submit_quiz(request, quiz_id):
    logger.debug(f"Submit Quiz view called for quiz_id: {quiz_id}")

    # Check if the user has already completed this quiz
    try:
        attempt = QuizAttempt.objects.get(user=request.user, quiz=quiz_id, is_completed=True)
        logger.info(f"User {request.user} has already completed quiz {quiz_id}. Redirecting to results.")
        
        # Calculate percentage
        score = attempt.score
        total_questions = attempt.quiz.questions.count()
        percentage = (score / total_questions) * 100
        
        return render(request, 'quiz_result.html', {
            'quiz': attempt.quiz,
            'score': score,
            'total': total_questions,
            'percentage': percentage,
        })
    except QuizAttempt.DoesNotExist:
        pass  # User hasn't completed this quiz, allow them to submit

    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all()
        score = 0
        total_questions = questions.count()

        logger.debug(f"Quiz retrieved: {quiz.title} with {total_questions} questions")

        try:
            attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, score=0, is_completed=False)
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

        # Update the attempt with the final score and mark it as completed
        attempt.score = score
        attempt.is_completed = True
        try:
            attempt.save()
            logger.info(f"QuizAttempt updated with final score: {score} and marked as completed for user: {request.user}")
        except Exception as e:
            logger.error(f"Error updating QuizAttempt with final score: {e}")

        # Calculate percentage
        percentage = (score / total_questions) * 100

        # Render the results on the same page
        return render(request, 'quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total': total_questions,
            'percentage': percentage,
        })

    return redirect('quiz_detail', quiz_id=quiz_id)

# User registration view
def register(request):
    logger.debug(f"Register view called")
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login success view
def login_success_view(request):
    logger.debug(f"Login view called")
    return redirect('home')

@staff_member_required
def quiz_results_view(request):
    logger.debug("Quiz results view called")
    if not request.user.is_staff:
        return redirect('home')
    
    # Gets filters from the request
    user_filter = request.GET.get('user')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    score_min = request.GET.get('score_min')
    score_max = request.GET.get('score_max')
    quiz_filter = request.GET.get('quiz')
    sort_by = request.GET.get('sort_by', 'date_taken')

    # Initial filter based on specific fields
    attempts = QuizAttempt.objects.all()

    if user_filter and user_filter != 'None':
        attempts = attempts.filter(user__username__icontains=user_filter)
    
    if quiz_filter and quiz_filter != 'None':
        attempts = attempts.filter(quiz__title__icontains=quiz_filter)
    
    if date_from and date_from != 'None':
        attempts = attempts.filter(date_taken__gte=parse_date(date_from))
    
    if date_to and date_to != 'None':
        attempts = attempts.filter(date_taken__lte=parse_date(date_to))
    
    if score_min and score_min != 'None':
        attempts = attempts.filter(score__gte=int(score_min))
    
    if score_max and score_max != 'None':
        attempts = attempts.filter(score__lte(int(score_max)))
    
    # Implement the search functionality here
    search_query = request.GET.get('search')
    if search_query and search_query != 'None':
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

# View to display details of a specific quiz attempt, requires login
@login_required
def quiz_attempt_detail(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)  # Get the quiz attempt or return 404 if not found
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

# View to handle user logout
def logout_view(request):
    logger.debug(f"Logout view called")
    logout(request)
    return redirect('home')

# View to display user profile, requires login
@login_required
def profile_view(request):
    is_admin = request.user.is_staff  # Check if the user is an admin
    return render(request, 'profile.html', {'is_admin': is_admin})

# View to handle editing user profile, requires login
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

# View to handle changing user password, requires login
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

# View to reset a specific quiz attempt, requires login and staff status
@login_required
def reset_quiz_attempt(request, attempt_id):
    if request.method == 'POST' and request.user.is_staff:
        try:
            attempt = QuizAttempt.objects.get(id=attempt_id)
            attempt.delete()  # This deletes the existing quiz attempt
            messages.success(request, "The quiz attempt has been reset successfully.")
        except QuizAttempt.DoesNotExist:
            messages.error(request, "Quiz attempt not found.")
        return redirect('home')  # Redirects to the home page after resetting
    else:
        return redirect('home')  # Redirects to home if the request is not POST or user is not an admin

# View to export quiz results as a CSV file, requires staff status
@staff_member_required
def export_quiz_results_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="quiz_results.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['User', 'Quiz Title', 'Score', 'Total Questions', 'Percentage', 'Date Taken'])

    quiz_attempts = QuizAttempt.objects.all()

    for attempt in quiz_attempts:
        total_questions = attempt.quiz.questions.count()
        percentage = (attempt.score / total_questions) * 100 if total_questions > 0 else 0
        writer.writerow([
            attempt.user.username,
            attempt.quiz.title,
            attempt.score,
            total_questions,
            f'{percentage:.2f}%',
            attempt.date_taken.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response

# View to reset filters for the quiz results view, requires staff status
@staff_member_required
def reset_filters(request):
    return redirect('quiz_results')
