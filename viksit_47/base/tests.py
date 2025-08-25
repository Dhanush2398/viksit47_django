from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Mock, Question, Option, MockResult


class MockExamTests(TestCase):

    def setUp(self):
        # Test user
        self.user = User.objects.create_user(username="testuser", password="password123")

        # Mock exam
        self.mock = Mock.objects.create(
            title="Math Test",
            time_limit=30,
            difficulty="easy"
        )

        # Question + options
        self.q1 = Question.objects.create(mock=self.mock, text="2 + 2 = ?")
        self.o1 = Option.objects.create(question=self.q1, text="3", is_correct=False)
        self.o2 = Option.objects.create(question=self.q1, text="4", is_correct=True)

        self.client = Client()

    def test_register_user(self):
        response = self.client.post(reverse("register"), {
            "username": "newuser",
            "password1": "newpassword123",
            "password2": "newpassword123"
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_user(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_access_mock_page_requires_login(self):
        response = self.client.get(reverse("mock", args=[self.mock.id]))
        self.assertRedirects(response, "/login/?next=/mock/{}/".format(self.mock.id))

    def test_submit_mock_all_correct(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse("submit_mock", args=[self.mock.id]), {
            f"q{self.q1.id}": self.o2.id  # Correct answer
        })
        self.assertEqual(response.status_code, 200)
        result = MockResult.objects.filter(user=self.user, mock=self.mock).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.total, 1)
        self.assertEqual(result.attempted, 1)
        self.assertEqual(result.correct, 1)
        self.assertEqual(result.score, 100.0)

    def test_submit_mock_incorrect_answer(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse("submit_mock", args=[self.mock.id]), {
            f"q{self.q1.id}": self.o1.id  # Wrong answer
        })
        self.assertEqual(response.status_code, 200)
        result = MockResult.objects.filter(user=self.user, mock=self.mock).first()
        self.assertEqual(result.correct, 0)
        self.assertEqual(result.score, 0.0)

    def test_submit_mock_unattempted(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse("submit_mock", args=[self.mock.id]), {})
        self.assertEqual(response.status_code, 200)
        result = MockResult.objects.filter(user=self.user, mock=self.mock).first()
        self.assertEqual(result.attempted, 0)
        self.assertEqual(result.correct, 0)
        self.assertEqual(result.score, 0.0)

    def test_profile_shows_results(self):
        self.client.login(username="testuser", password="password123")
        # create a result manually
        MockResult.objects.create(user=self.user, mock=self.mock, total=1, attempted=1, correct=1)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Math Test")
