from django.shortcuts import render, get_object_or_404
from .models import Quiz, Question

def home(request):
    quizzes = Quiz.objects.all()
    return render(request, 'home.html', {'quizzes': quizzes})

def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    
    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_option = request.POST.get(str(question.id))
            if selected_option == question.correct_option:
                score += 1
        return render(request, 'quiz_result.html', {'quiz': quiz, 'score': score, 'total': len(questions)})

    return render(request, 'quiz_detail.html', {'quiz': quiz, 'questions': questions})

def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # Logic to calculate score
    return render(request, 'quiz_result.html', {'quiz': quiz})
