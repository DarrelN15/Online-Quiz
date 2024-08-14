from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title

class Option(models.Model):
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Question(models.Model):
    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    QUESTION_TYPES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)
    options = models.ManyToManyField(Option, related_name='questions')
    correct_options = models.ManyToManyField(Option, related_name='correct_for')
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default=SINGLE_CHOICE)
    title = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.quiz.title} - Score: {self.score}'

class QuestionResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(Option)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.question.text} - {self.is_correct}'
