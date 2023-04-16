import datetime
from django.test import TestCase
from django.urls import reverse
from .models import Course, User
from .forms import requestCourseForm, searchCourseForm

class Request_Course_Form(TestCase):
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

#     def test_repeated_course(self):
#         test_user = User.objects.get(username="emilychang")
#         c = Course(username=test_user, course_institution="Auburn University", course_name="Statics",
#                    course_dept="ENGR", course_num=2050, course_grade='A', course_delivery="IN-PERSON",
#                    syllabus_url="https://www.google.com/", credit_hours=3)
#         c.save()
#         form_data = {'course_institution': 'University of Virginia', 'course_name': 'Advanced Software Development',
#                      'course_dept': 'C S', 'course_number': '1000', 'course_grade': 'A', 'course_delivery': 'IN-PERSON',
#                      'syllabus_url': 'https://docs.djangoproject.com/en/4.1/topics/db/models/', 'credit_hours': '100'}
#         c.delete()

class LoginViewTests(TestCase):
    def test_login_load(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

# class CourseListTests(TestCase):
#     def test_course_list_load(self):
#         response = self.client.get(reverse('requestCourseList'))
#         self.assertEqual(response.status_code, 200)

# command should be: python manage.py test --keepdb