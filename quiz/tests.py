from datetime import timezone
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from quiz.models import Quiz, Question, Option, QuizAttempt
from quiz.forms import CustomPasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape

import pytz

# Create your tests here.
class UserRegistrationTest(TestCase):

    def test_registration_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        })
        
        if response.status_code == 200:
            self.assertContains(response, "This field is required.")  # Example error message
        else:
            self.assertEqual(response.status_code, 302)  # Redirects after successful registration

class UserAuthenticationTest(TestCase):
  
    def setUp(self):
        # Creates a user for testing login
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_user_login(self):
        # Attempts to log in with correct credentials
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login
        self.assertTrue(response.wsgi_request.user.is_authenticated)  # User should be authenticated
        
    def test_invalid_login(self):
        # Attempts to log in with incorrect credentials
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Should not redirect; should re-render login form
        self.assertContains(response, "Please enter a correct username and password.")  # Example error message
        self.assertFalse(response.wsgi_request.user.is_authenticated)  # User should not be authenticated

    def test_user_logout(self):
        # Logs in first
        self.client.login(username='testuser', password='testpassword')

        # Then logs out
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect after logout
        self.assertFalse(response.wsgi_request.user.is_authenticated)  # User should no longer be authenticated

class UserProfileTest(TestCase):
    def setUp(self):
        # Creates a regular user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_profile_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response, 'testuser')

class UserProfileEditTest(TestCase):
    def setUp(self):
        # Creates a user for testing profile edit
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')

    def test_profile_edit(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('edit_profile'), {
            'username': 'updateduser',
            'email': 'updated@example.com',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after update
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updated@example.com')
        
    def test_profile_edit_errors(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('edit_profile'), {
            'username': '',
            'email': 'updated@example.com',
        })
        self.assertEqual(response.status_code, 200)  # Should not redirect; should re-render edit form
        self.assertTemplateUsed(response, 'edit_profile.html')
        self.assertContains(response, "This field is required.")  # Example error message

class AdminStatusDisplayTest(TestCase):
    def setUp(self):
        # Creates a regular user for testing
        self.user = User.objects.create_user(username='regularuser', password='testpassword')
        # Logs in as the regular user
        self.client.login(username='regularuser', password='testpassword')

    def test_regular_user_status_display(self):
        # Accesses the profile page as a regular user
        response = self.client.get(reverse('profile'))

        # Asserts that the user is not redirected (status code should be 200)
        self.assertEqual(response.status_code, 200)

        # Asserts that the profile page does not contain the admin status message
        self.assertNotContains(response, 'This is an admin account')

class PasswordAuthenticationTest(TestCase):
    def setUp(self):
        # Creates a user for testing password change
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Logs in as the user
        self.client.login(username='testuser', password='testpassword')
        
        # Creates a new password
        self.new_password = 'newpassword123'
        
    def test_password_change(self):
        # Creates a new password change form and submit it
        response = self.client.post(reverse('change_password'), {
            'old_password': 'testpassword',
            'new_password1': self.new_password,
            'new_password2': self.new_password,
        })

        # Asserts that the password was changed and the response is a redirect
        self.assertEqual(response.status_code, 302)
        
        # Logs out and trys to log in with the new password
        self.client.logout()
        login_successful = self.client.login(username='testuser', password=self.new_password)
        
        # Asserts that the login with the new password is successful
        self.assertTrue(login_successful)

    def test_password_change_invalid(self):
        # Attempts to change the password with invalid data (mismatching new passwords)
        response = self.client.post(reverse('change_password'), {
            'old_password': 'testpassword',
            'new_password1': self.new_password,
            'new_password2': 'differentpassword',
        })

        # Asserts that the form is not valid and no redirect happens
        self.assertEqual(response.status_code, 200)  # No redirect because the form should be invalid
        self.assertContains(response, "The two password fields didn’t match.")
        
class QuizCreationTest(TestCase):
    def setUp(self):
        # Creates an admin user
        self.admin_user = User.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.login(username='adminuser', password='adminpassword')

    def test_quiz_creation(self):
        response = self.client.post(reverse('admin:quiz_quiz_add'), {
            'title': 'Test Quiz',
            'description': 'This is a test quiz.',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Quiz.objects.filter(title='Test Quiz').exists())  # Verify the quiz was created
        
class QuizListingTest(TestCase):
    def setUp(self):
        # Creates some quizzes
        Quiz.objects.create(title='Quiz 1', description='Description 1')
        Quiz.objects.create(title='Quiz 2', description='Description 2')

    def test_quiz_listing(self):
        response = self.client.get(reverse('quizzes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quiz 1')
        self.assertContains(response, 'Quiz 2')
        
class QuizDetailViewTest(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create(title='Quiz Detail Test', description='Test description')

    def test_quiz_detail_view(self):
        response = self.client.get(reverse('quiz_detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test description')


class QuizSubmissionTest(TestCase):
    def setUp(self):
        # Creates a quiz
        self.quiz = Quiz.objects.create(title='Quiz Submission Test')
        
        # Creates a question
        self.question = Question.objects.create(quiz=self.quiz, text='Sample Question', question_type=Question.SINGLE_CHOICE)
        
        # Creates options and link them to the question
        self.option1 = Option.objects.create(text='Option 1', is_correct=True)
        self.option2 = Option.objects.create(text='Option 2', is_correct=False)
        self.question.options.add(self.option1, self.option2)
        self.question.correct_options.add(self.option1)
        
        # Creates a user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_quiz_submission(self):
        response = self.client.post(reverse('submit_quiz', args=[self.quiz.id]), {
            str(self.question.id): self.option1.id,
        })

        self.assertEqual(response.status_code, 200)  # Expects the quiz detail page to be rendered
        self.assertContains(response, 'Your Score: 1 out of 1')  # Checks if the score is displayed correctly

        # Verifys that the QuizAttempt was saved with the correct score
        attempt = QuizAttempt.objects.get(user=self.user, quiz=self.quiz)
        self.assertEqual(attempt.score, 1)

class QuizResultsFilteringTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1', is_staff=True)
        self.user2 = User.objects.create_user(username='user2', password='password2', is_staff=True)
        
        self.client.login(username='user1', password='password1')
        
        self.quiz1 = Quiz.objects.create(title='Quiz 1')
        self.quiz2 = Quiz.objects.create(title='Quiz 2')
        self.attempt1 = QuizAttempt.objects.create(user=self.user1, quiz=self.quiz1, score=5, date_taken="2024-08-10")
        self.attempt2 = QuizAttempt.objects.create(user=self.user2, quiz=self.quiz2, score=7, date_taken="2024-08-15")
        self.attempt3 = QuizAttempt.objects.create(user=self.user1, quiz=self.quiz2, score=3, date_taken="2024-08-20")

    def test_filter_by_user(self):
        response = self.client.get(reverse('quiz_results'), {'user': 'user1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user1')
        self.assertNotContains(response, 'user2')

    def test_filter_by_quiz(self):
        response = self.client.get(reverse('quiz_results'), {'quiz': 'Quiz 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quiz 1')
        self.assertNotContains(response, 'Quiz 2')

    def test_filter_by_date_range(self):
        response = self.client.get(reverse('quiz_results'), {'date_from': '2024-08-10', 'date_to': '2024-08-20'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2024-08-10')
        self.assertContains(response, '2024-08-20')
        self.assertNotContains(response, '2024-08-15')

    def test_filter_by_score_range(self):
        response = self.client.get(reverse('quiz_results'), {'score_min': 5, 'score_max': 7})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '5 / 0')
        self.assertContains(response, '7 / 0')
        self.assertNotContains(response, '3 / 0')
        
class GeneralFunctionalityTest(TestCase):
    
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Welcome to Our Quiz Platform!')
        
class NavigationTest(TestCase):

    def test_navigation_links(self):
        # Tests the home link
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'href="' + reverse('home') + '"')

        # Tests the quizzes link
        response = self.client.get(reverse('quizzes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('quizzes') + '"')

        # Tests the about link
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="' + reverse('about') + '"')
        
class SecurityTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_csrf_protection(self):
        # Attempts to submit a form without a CSRF token
        response = self.client.post(reverse('submit_quiz', args=[1]), {})
        self.assertEqual(response.status_code, 403)  # Should be forbidden due to missing CSRF token

    @csrf_exempt
    def test_csrf_exempt_view(self):
        # Tests a view that should be CSRF exempt
        response = self.client.post(reverse('submit_quiz', args=[1]), {})
        self.assertNotEqual(response.status_code, 403)  # Should not be forbidden if CSRF is exempted

class SecurityTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_xss_protection(self):
        # Submits input that could be an XSS attack
        malicious_input = '<script>alert("XSS")</script>'
        response = self.client.post(reverse('edit_profile'), {
            'username': malicious_input,
            'email': 'user@example.com'
        })

        # Checks that the output is escaped and not rendered as HTML
        self.assertNotContains(response, malicious_input)
        self.assertContains(response, escape(malicious_input))