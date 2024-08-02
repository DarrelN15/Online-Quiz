import random
from django.shortcuts import render, get_object_or_404
from .models import Quiz, Question, Option

def home(request):
    # Retrieve all quizzes from the database
    quizzes = Quiz.objects.all()
    # Render the home template with the list of quizzes
    return render(request, 'home.html', {'quizzes': quizzes})

def quiz_detail(request, quiz_id):
    # Get the specific quiz by its ID or return a 404 if not found
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # Retrieve all questions related to this quiz
    questions = quiz.questions.all()

    # Shuffle options for each question to randomize the order
    for question in questions:
        options = list(question.options.all())  # Get all options for the question
        random.shuffle(options)  # Shuffle the list of options
        question.shuffled_options = options  # Assign shuffled options to the question

    # Check if the request is a POST (form submission)
    if request.method == 'POST':
        score = 0  # Initialize score counter
        # Iterate through each question to calculate the score
        for question in questions:
            # Get the list of selected option IDs for the question from the POST data
            selected_option_ids = request.POST.getlist(str(question.id))
            # Retrieve the Option objects for the selected option IDs
            selected_options = Option.objects.filter(id__in=selected_option_ids)
            # Retrieve the correct options for the question
            correct_options = question.correct_options.all()

            # If selected options match the correct options, increment the score
            if set(selected_options) == set(correct_options):
                score += 1

        # Render the quiz result template with the score and total number of questions
        return render(request, 'quiz_result.html', {'quiz': quiz, 'score': score, 'total': len(questions)})

    # Render the quiz detail template with the quiz and its questions
    return render(request, 'quiz_detail.html', {'quiz': quiz, 'questions': questions})

def quiz_result(request, quiz_id):
    # Get the specific quiz by its ID or return a 404 if not found
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # Render the quiz result template for the specified quiz
    return render(request, 'quiz_result.html', {'quiz': quiz})
