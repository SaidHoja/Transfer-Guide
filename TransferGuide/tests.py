import datetime
from django.test import TestCase
from django.urls import reverse
from .models import Course

class FormViewTests(TestCase):
    def test_form_load(self):
        response = self.client.get(reverse('addCourse'))
        self.assertEqual(response.status_code, 200)

class TryAgainViewTests(TestCase):
    def test_try_again_load(self):
        response = self.client.get(reverse('tryAgain'))
        self.assertEqual(response.status_code, 200)

class LoginViewTests(TestCase):
    def test_login_load(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

class CourseListTests(TestCase):
    def test_course_list_load(self):
        response = self.client.get("/addCourse/list")
        self.assertEqual(response.status_code, 200)

# command should be: python manage.py test --keepdb