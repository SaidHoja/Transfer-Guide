import datetime
from django.test import TestCase
from django.urls import reverse
from .models import Course
from .forms import addCourseForm

class FormViewTests(TestCase):
    def test_form_load(self):
        response = self.client.get(reverse('addCourse'))
        self.assertEqual(response.status_code, 200)
    def test_all_no_response(self):
        form_data = {'course_institution':'','course_name':'','course_dept':'','course_number':'','course_grade':''}
        form = addCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_one_no_response(self):
        form_data = {'course_institution': 'University of Virginia', 'course_name': 'Advanced Software Development',
                     'course_dept': 'CS', 'course_number': '','course_grade': 'A'}
        form = addCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_all_response(self):
        form_data = {'course_institution': 'University of Virginia', 'course_name': 'Advanced Software Development',
                     'course_dept': 'CS', 'course_number': '3240','course_grade': 'A'}
        form = addCourseForm(data=form_data)
        self.assertTrue(form.is_valid())

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