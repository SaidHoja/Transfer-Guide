import datetime
from django.test import TestCase
from django.urls import reverse
from .models import Course
from .forms import requestCourseForm, searchCourseForm

class FormViewTests(TestCase):
    def test_form_load(self):
        response = self.client.get(reverse('requestCourse'))
        self.assertEqual(response.status_code, 200)
    def test_all_no_response(self):
        form_data = {'course_institution':'','course_name':'','course_dept':'','course_number':'','course_grade':'',
                     'course_delivery':'','syllabus_url':'','credit_hours':''}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_one_no_response(self):
        form_data = {'course_institution':'University of Virginia', 'course_name':'Advanced Software Development',
                     'course_dept':'CS', 'course_number':'1000','course_grade':'A','course_delivery':'IN-PERSON',
                     'syllabus_url':'','credit_hours':'4'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_all_response(self):
        form_data = {'course_institution':'University of Virginia', 'course_name':'Advanced Software Development',
                     'course_dept':'CS', 'course_number':'1000','course_grade':'A','course_delivery':'IN-PERSON',
                     'syllabus_url':'https://docs.djangoproject.com/en/4.1/topics/db/models/','credit_hours':'4'}
        form = requestCourseForm(data=form_data)
        self.assertTrue(form.is_valid())
    def test_bad_url(self):
        form_data = {'course_institution': 'University of Virginia', 'course_name': 'Advanced Software Development',
                     'course_dept': 'CS', 'course_number': '1000', 'course_grade': 'A', 'course_delivery': 'IN-PERSON',
                     'syllabus_url': 'google', 'credit_hours': '4'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_bad_course_num(self):
        form_data = {'course_institution': 'University of Virginia', 'course_name': 'Advanced Software Development',
                     'course_dept': 'CS', 'course_number': '-1000', 'course_grade': 'A', 'course_delivery': 'IN-PERSON',
                     'syllabus_url': 'https://docs.djangoproject.com/en/4.1/topics/db/models/', 'credit_hours': '4'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_bad_dept(self):
        form_data = {'course_institution':'University of Virginia', 'course_name':'Advanced Software Development',
                     'course_dept':'C S', 'course_number':'1000','course_grade':'A','course_delivery':'IN-PERSON',
                     'syllabus_url':'https://docs.djangoproject.com/en/4.1/topics/db/models/','credit_hours':'4'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_bad_credit(self):
        form_data = {'course_institution':'University of Virginia', 'course_name':'Advanced Software Development',
                     'course_dept':'C S', 'course_number':'1000','course_grade':'A','course_delivery':'IN-PERSON',
                     'syllabus_url':'https://docs.djangoproject.com/en/4.1/topics/db/models/','credit_hours':'100'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
# class TryAgainViewTests(TestCase):
#     def test_try_again_load(self):
#         response = self.client.get(reverse('tryAgain'))
#         self.assertEqual(response.status_code, 200)

class LoginViewTests(TestCase):
    def test_login_load(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

class Search_Course_Form(TestCase):
    def test_blank_form(self):
        form_data = {"institution":"", "word":"", "dept_num":""}
        form = searchCourseForm(data=form_data)
        self.assertTrue(form.is_valid())
    def test_equivalence_case(self):
        form_data = {"institution":"Piedmont Virginia Community College", "word":"eq", "dept_num":"ENGR 1000"}
        form = searchCourseForm(data=form_data)
        self.assertTrue(form.is_valid())
    def test_invalid_dept_has_num(self):
        form_data = {"institution":"", "word":"", "dept_num":"4 1000"}
        form = searchCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_invalid_dept_invalid_char(self):
        form_data = {"institution":"", "word":"", "dept_num":"!! 1000"}
        form = searchCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_valid_dept_hetero_cases(self):
        form_data = {"institution":"", "word":"", "dept_num":"Engr 1000"}
        form = searchCourseForm(data=form_data)
        self.assertTrue(form.is_valid())
    def test_invalid_num_negative(self):
        form_data = {"institution": "", "word": "", "dept_num": "ENGR -1000"}
        form = searchCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_invalid_num_zero(self):
        form_data = {"institution": "", "word": "", "dept_num": "ENGR 0"}
        form = searchCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_invalid_num_too_small(self):
        form_data = {"institution": "", "word": "", "dept_num": "ENGR 1"}
        form = searchCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_invalid_num_uses_letters(self):
        form_data = {"institution": "", "word": "", "dept_num": "ENGR IS"}
        form = searchCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_invalid_num_exclamation(self):
        form_data = {"institution": "", "word": "", "dept_num": "ENGR !"}
        form = searchCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_invalid_too_many_words(self):
        form_data = {"institution": "", "word": "", "dept_num": "ENGR 1000 1"}
        form = searchCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
# class CourseListTests(TestCase):
#     def test_course_list_load(self):
#         response = self.client.get(reverse('requestCourseList'))
#         self.assertEqual(response.status_code, 200)

# command should be: python manage.py test --keepdb