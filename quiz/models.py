from django.db import models

class Quiz(models.Model):
    # Represents a quiz with a title and optional description
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        # Return the quiz title for display
        return self.title

class Option(models.Model):
    # Represents an answer option
    text = models.CharField(max_length=100)

    def __str__(self):
        # Return the option text for display
        return self.text

class Question(models.Model):
    # Constants for defining question types
    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    QUESTION_TYPES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
    ]

    # Links questions to a specific quiz and options
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)
    options = models.ManyToManyField(Option, related_name='questions')
    correct_options = models.ManyToManyField(Option, related_name='correct_for')
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default=SINGLE_CHOICE)

    def __str__(self):
        # Return the question text for display
        return self.text

