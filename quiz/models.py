from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Model representing a quiz
class Quiz(models.Model):
    title = models.CharField(max_length=200)  # Title of the quiz
    description = models.TextField()  # Description of the quiz

    def __str__(self):
        return self.title  # Returns the title of the quiz as its string representation

# Model representing an option for a quiz question
class Option(models.Model):
    text = models.CharField(max_length=200)  # Text of the option
    is_correct = models.BooleanField(default=False)  # Indicates if this option is correct

    def __str__(self):
        return self.text  # Returns the text of the option as its string representation

# Model representing a question in a quiz
class Question(models.Model):
    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    QUESTION_TYPES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')  # Link to the quiz this question belongs to
    text = models.CharField(max_length=255)  # Text of the question
    options = models.ManyToManyField(Option, related_name='questions')  # Options available for this question
    correct_options = models.ManyToManyField(Option, related_name='correct_for')  # Correct options for this question
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default=SINGLE_CHOICE)  # Type of the question (single or multiple choice)

    def __str__(self):
        return self.text  # Returns the text of the question as its string representation

# Model representing a user's attempt at taking a quiz
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who took the quiz
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)  # The quiz that was taken
    score = models.IntegerField()  # The user's score on the quiz
    date_taken = models.DateTimeField(auto_now_add=True)  # The date and time when the quiz was taken
    is_completed = models.BooleanField(default=False)  # Indicates if the quiz attempt has been completed

    def __str__(self):
        return f'{self.user.username} - {self.quiz.title} - Score: {self.score}'  # Returns a string representation of the quiz attempt

# Model representing a response to a question in a quiz attempt
class QuestionResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)  # The quiz attempt this response is part of
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # The question that was answered
    is_correct = models.BooleanField()  # Indicates if the response was correct
    selected_options = models.ManyToManyField(Option)  # The options selected by the user

    def __str__(self):
        return f'{self.question.text} - {self.is_correct}'  # Returns a string representation of the question response
