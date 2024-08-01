from django.shortcuts import render, get_object_or_404
from .models import Quiz, Question, Option

def home(request):
    quizzes = Quiz.objects.all()
    return render(request, 'home.html', {'quizzes': quizzes})

def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_options = request.POST.getlist(str(question.id))
            correct_options = question.correct_options.all()
            if question.question_type == Question.SINGLE_CHOICE:
                if selected_options[0] in correct_options.values_list('id', flat=True):
                    score += 1
            elif question.question_type == Question.MULTIPLE_CHOICE:
                if set(selected_options) == set(correct_options.values_list('id', flat=True)):
                    score += 1
        return render(request, 'quiz_result.html', {'quiz': quiz, 'score': score, 'total': len(questions)})

    return render(request, 'quiz_detail.html', {'quiz': quiz, 'questions': questions})

def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'quiz_result.html', {'quiz': quiz})
