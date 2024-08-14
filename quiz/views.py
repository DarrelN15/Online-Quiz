from django.http import HttpResponse
import random
from django.shortcuts import render, get_object_or_404
from .models import Quiz, Question, Option, QuizAttempt, QuestionResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.core.paginator import Paginator
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
    # logger.info(f"Submit quiz view called for quiz_id: {quiz_id} by user: {request.user}")

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
            
            # Log each question's response
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

        return render(request, 'quiz_results.html', {'quiz': quiz, 'score': score, 'total': total_questions})
    
    # If it's not a POST request, redirect to the quiz detail page
    logger.warning(f"Non-POST request received for submit_quiz view for quiz_id: {quiz_id}")
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

@staff_member_required
def quiz_results_view(request):
    logger.debug(f"Quiz results view called")
    if not request.user.is_staff:
        return redirect('home')
    attempts = QuizAttempt.objects.all().order_by('-date_taken')
    return render(request, 'quiz_results.html', {'attempts': attempts})

def logout_view(request):
    logger.debug(f"Logout view called")
    logout(request)
    return redirect('home')