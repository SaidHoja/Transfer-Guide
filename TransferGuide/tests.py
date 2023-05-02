import datetime
from django.test import TestCase
from django.urls import reverse

from .models import Course, User, UVA_Course, Request
from .forms import requestCourseForm, searchCourseForm, viableCourseForm, sisForm
from .views import return_transfer_courses, doesCourseExist
import unittest

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
        form_data = {'course_institution':'University of Pittsburgh', 'course_name':'Advanced Software Development',
                     'course_dept':'CS', 'course_number':'1000','course_grade':'A','course_delivery':'IN-PERSON',
                     'syllabus_url':'','credit_hours':'4'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_all_response(self):
        form_data = {'course_institution':'University of Pittsburgh', 'course_name':'Advanced Software Development',
                     'course_dept':'CS', 'course_number':'1000','course_grade':'A','course_delivery':'IN-PERSON',
                     'syllabus_url':'https://docs.djangoproject.com/en/4.1/topics/db/models/','credit_hours':'4'}
        form = requestCourseForm(data=form_data)
        self.assertTrue(form.is_valid())
    def test_bad_url(self):
        form_data = {'course_institution': 'University of Pittsburgh', 'course_name': 'Advanced Software Development',
                     'course_dept': 'CS', 'course_number': '1000', 'course_grade': 'A', 'course_delivery': 'IN-PERSON',
                     'syllabus_url': 'google', 'credit_hours': '4'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_bad_course_num(self):
        form_data = {'course_institution': 'University of Pittsburgh', 'course_name': 'Advanced Software Development',
                     'course_dept': 'CS', 'course_number': '-1000', 'course_grade': 'A', 'course_delivery': 'IN-PERSON',
                     'syllabus_url': 'https://docs.djangoproject.com/en/4.1/topics/db/models/', 'credit_hours': '4'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_bad_dept(self):
        form_data = {'course_institution':'University of Pittsburgh', 'course_name':'Advanced Software Development',
                     'course_dept':'C S', 'course_number':'1000','course_grade':'A','course_delivery':'IN-PERSON',
                     'syllabus_url':'https://docs.djangoproject.com/en/4.1/topics/db/models/','credit_hours':'4'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_bad_credit(self):
        form_data = {'course_institution':'University of Pittsburgh', 'course_name':'Advanced Software Development',
                     'course_dept':'C S', 'course_number':'1000','course_grade':'A','course_delivery':'IN-PERSON',
                     'syllabus_url':'https://docs.djangoproject.com/en/4.1/topics/db/models/','credit_hours':'100'}
        form = requestCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    # def test_bad_institution(self):
    #     form_data = {'course_institution': 'University of Virginia', 'course_name': 'Advanced Software Development',
    #                  'course_dept': 'CS', 'course_number': '1000', 'course_grade': 'A',
    #                  'course_delivery': 'IN-PERSON',
    #                  'syllabus_url': 'https://docs.djangoproject.com/en/4.1/topics/db/models/', 'credit_hours': '4'}
    #     form = requestCourseForm(data=form_data)
    #     self.assertFalse(form.is_valid())

class SIS_Form(TestCase):
    def test_instructor_as_nonChar(self):
        form_data = {'subject':'' , 'terms':'FALL' , 'year':'2000' , 'instructor':'%'}
        form = sisForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_instructor_as_num(self):
        form_data = {'subject': '', 'terms': 'FALL', 'year': '2000', 'instructor': 'm1'}
        form = sisForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_instructor_two_words(self):
        form_data = {'subject': '', 'terms': 'FALL', 'year': '2000', 'instructor': 'hui ma'}
        form = sisForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_instructor_one_word(self):
        form_data = {'subject': '', 'terms': 'FALL', 'year': '2000', 'instructor': 'ma'}
        form = sisForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_beta_ankit(self):
        form_data = {'subject':'APMA' , 'terms':'FALL' , 'year':'2023', 'instructor':'%%%'}
        form = sisForm(data=form_data)
        self.assertFalse(form.is_valid())
    # def test_no_subject_no_instructor(self):
    #     form_data = {'subject':'', 'terms': 'FALL', 'year':'2000', 'instructor':''}
    #     form = sisForm(data=form_data)
    #     self.assertTrue(form.is_valid())
    def test_subject_as_num(self):
        form_data = {'subject': '1', 'terms': 'FALL', 'year':'2000', 'instructor':''}
        form = sisForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_subject_as_nonAlpha(self):
        form_data = {'subject': '%', 'terms': 'FALL', 'year': '2000', 'instructor': ''}
        form = sisForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_subject_as_two_words(self):
        form_data = {'subject': 'M I', 'terms': 'FALL', 'year': '2000', 'instructor': ''}
        form = sisForm(data=form_data)
        self.assertFalse(form.is_valid())
# class Request_New_Course(unittest.TestCase):
#     instances = []
#     user_courses = []
#     @classmethod
#     def setUpClass(cls):
#         me = User.objects.get(username="emilychang")
#         person1 = User.objects.get(username="fyg6db")
#         person2 = User.objects.get(username="dagim")
#         person3 = User.objects.get(username="suhayla")
#         cls.course1 = Course.objects.create(username=me, course_institution="University of Central Arkansas",
#                                             course_name="Ordinary Diff Equations", course_dept="MATH", course_num=331,
#                                             course_grade='A', course_delivery="IN-PERSON",
#                                             syllabus_url="https://www.google.com/", credit_hours=3)
#         cls.course2 = Course.objects.create(username=person1, course_institution="University of Central Arkansas",
#                                             course_name="Ordinary Diff Equations", course_dept="MATH", course_num=331,
#                                             course_grade='D', course_delivery="IN-PERSON",
#                                             syllabus_url="https://www.google.com/", credit_hours=3)
#         cls.course3 = Course.objects.create(username=person2, course_institution="University of Central Arkansas",
#                                             course_name="Ordinary Diff Equations", course_dept="MATH", course_num=331,
#                                             course_grade='C', course_delivery="IN-PERSON",
#                                             syllabus_url="https://www.google.com/", credit_hours=3)
#         cls.course4 = Course.objects.create(username=person3, course_institution="Harvard College",
#                                             course_name="Advanced Mathematics", course_dept="MATH", course_num=331,
#                                             course_grade='B', course_delivery="IN-PERSON",
#                                             syllabus_url="https://www.google.com/", credit_hours=3)
#         cls.instances.append(cls.course1)
#         cls.instances.append(cls.course2)
#         cls.instances.append(cls.course3)
#         cls.instances.append(cls.course4)
#         cls.request1 = Request.objects.create(uva_course=UVA_Course.objects.get(course_dept="APMA", course_num=2130),
#                                               foreign_course=Course.objects.get(course_name="Ordinary Diff Equations", course_grade='A',),
#                                               status='A', credit_hours=3, reviewed_by=me)
#         cls.request2 = Request.objects.create(uva_course=UVA_Course.objects.get(course_dept="APMA", course_num=2130),
#                                               foreign_course=Course.objects.get(course_name="Ordinary Diff Equations", course_grade='D'),
#                                               status='D', credit_hours=3, reviewed_by=me)
#         cls.request3 = Request.objects.create(uva_course=UVA_Course.objects.get(course_dept="APMA", course_num=2130),
#                                               foreign_course=Course.objects.get(course_name="Ordinary Diff Equations", course_grade='C'),
#                                               status='P', credit_hours=3, reviewed_by=me)
#         cls.request4 = Request.objects.create(uva_course=UVA_Course.objects.get(course_dept="APMA", course_num=2130),
#                                               foreign_course=Course.objects.get(course_name="Advanced Mathematics"),
#                                               status='P', credit_hours=3, reviewed_by=me)
#         cls.instances.append(cls.request1)
#         cls.instances.append(cls.request2)
#         cls.instances.append(cls.request3)
#         cls.instances.append(cls.request4)
#         cls.user_courses = Course.objects.filter(id__in=[cls.course1.id, cls.course2.id, cls.course3.id, cls.course4.id])
#
#     def test_new_course_equivalence(self):
#         self.assertTrue(isRequestNew(self.user_courses, "MATH", 251, "Fullerton College"))
#     def test_new_course_same_college(self):
#         self.assertTrue(isRequestNew(self.user_courses, "ENGR", 1624, "University of Central Arkansas"))
#     def test_new_course_same_dept(self):
#         self.assertTrue(isRequestNew(self.user_courses, "MATH", 1624, "Harvard College"))
#     def test_new_course_same_dept_num(self):
#         self.assertTrue(isRequestNew(self.user_courses, "MATH", 331, "Columbia University"))
#     def test_invalid_course_submitted_Before(self):
#         self.assertFalse(isRequestNew(self.user_courses, "MATH", 331, "Harvard College"))
#     def test_invalid_course_preapproved(self):
#         self.assertFalse(isRequestNew(self.user_courses, "MATH", 331, "University of Central Arkansas"))
#     @classmethod
#     def tearDownClass(cls):
#         for instance in cls.instances:
#             instance.delete()
class Viable_Course_Form(TestCase):
    def test_form_load(self):
        response = self.client.get(reverse('submitViableCourse'))
        self.assertEqual(response.status_code, 200)
    def test_all_fields_filled(self):
        form_data = {'course_institution':'University of Central Arkansas','course_name':'Calculus II',
                     'course_dept':'MATH','course_number':1592,'course_grade':'B'}
        form = viableCourseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_most_fields_not_filled(self):
        form_data = {'course_institution': '', 'course_name': '',
                     'course_dept': '', 'course_number':0, 'course_grade': ''}
        form = viableCourseForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_one_field_unfilled(self):
        form_data = {'course_institution': 'University of Central Arkansas', 'course_name': 'Calculus II',
                     'course_dept': '', 'course_number': 1592, 'course_grade': 'B'}
        form = viableCourseForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_dept_too_many_words(self):
        form_data = {'course_institution': 'University of Central Arkansas', 'course_name': 'Calculus II',
                     'course_dept': 'MATH IS', 'course_number': 1592, 'course_grade': 'B'}
        form = viableCourseForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_dept_invalid_char(self):
        form_data = {'course_institution': 'University of Central Arkansas', 'course_name': 'Calculus II',
                     'course_dept': 'M@TH', 'course_number': 1592, 'course_grade': 'B'}
        form = viableCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_invalid_num_not_num(self):
        form_data = {'course_institution': 'University of Central Arkansas', 'course_name': 'Calculus II',
                     'course_dept': 'MATH', 'course_number':'AH', 'course_grade': 'B'}
        form = viableCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_invalid_num_is_negative(self):
        form_data = {'course_institution': 'University of Central Arkansas', 'course_name': 'Calculus II',
                     'course_dept': 'MATH', 'course_number': -1, 'course_grade': 'B'}
        form = viableCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_invalid_num_is_decimal(self):
        form_data = {'course_institution': 'University of Central Arkansas', 'course_name': 'Calculus II',
                     'course_dept': 'MATH', 'course_number': 1000.1, 'course_grade': 'B'}
        form = viableCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
    def test_course_num_is_0(self):
        form_data = {'course_institution': 'University of Central Arkansas', 'course_name': 'Calculus II',
                     'course_dept': 'MATH', 'course_number': -0, 'course_grade': 'B'}
        form = viableCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
class LoginViewTests(TestCase):
    def test_login_load(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

class Search_Course_Form(TestCase):
    def test_form_load(self):
        response = self.client.get(reverse('searchForCourse'))
        self.assertEqual(response.status_code, 200)
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
    def test_invalid_num_too_big(self):
        form_data = {"institution": "", "word": "", "dept_num": "ENGR 10000"}
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
# class Search_For_Course(unittest.TestCase):
#     instances = []
#     request = Request.objects.none()
#     @classmethod
#     def setUpClass(cls):
#         me = User.objects.get(username="emilychang")
#         cls.instances.append(Course.objects.create(username=me, course_institution="Auburn University", course_name="Statics",
#                                                     course_dept="ENGR", course_num=2050, course_grade='A',
#                                                     course_delivery="IN-PERSON",syllabus_url="https://www.google.com/",
#                                                     credit_hours=3))
#         cls.instances.append(Course.objects.create(username=me, course_institution="Northern Arizona University",
#                                                     course_name="Prin of Programming", course_dept="CSE", course_num=110,
#                                                     course_grade='B', course_delivery="IN-PERSON",syllabus_url="https://www.google.com/",
#                                                     credit_hours=3))
#         cls.instances.append(UVA_Course.objects.create(course_name="Outdated Materials Science Class",course_dept="MAE",
#                                                         course_num=2300,credit_hours=3))
#         cls.instances.append(UVA_Course.objects.create(course_name="Introduction to Programming", course_dept="CS",
#                                                         course_num=1110, credit_hours=3))
#         cls.request1 = Request.objects.create(uva_course=UVA_Course.objects.get(course_name="Outdated Materials Science Class"),
#                                                foreign_course=Course.objects.get(course_name="Statics"), status='A',
#                                                credit_hours=3, reviewed_by=me)
#         cls.request2 = Request.objects.create(uva_course=UVA_Course.objects.get(course_name="Introduction to Programming"),
#                                                foreign_course=Course.objects.get(course_name="Prin of Programming"), status='A',
#                                                credit_hours=3,reviewed_by=me)
#         cls.instances.append(cls.request1)
#         cls.instances.append(cls.request2)
#         cls.request = Request.objects.filter(id__in=[cls.request1.id, cls.request2.id])
#
#     @classmethod
#     def tearDownClass(cls):
#         for instance in cls.instances:
#             instance.delete()
#     def test_no_inputs(self):
#         result = return_transfer_courses("", "No Preference", self.request, "")
#         self.assertEqual(len(result), len(self.request))
#
#     def test_non_matching_word_case(self):
#         result = return_transfer_courses("", "No Preference", self.request, "pRoGrAmMing")
#         self.assertEqual(len(result), 1)
#     def test_non_matching_dept_case(self):
#         result = return_transfer_courses("MaE 2300", "No Preference", self.request, "")
#         self.assertEqual(len(result), 1)

# class CourseListTests(TestCase):
#     def test_course_list_load(self):
#         response = self.client.get(reverse('requestCourseList'))
#         self.assertEqual(response.status_code, 200)

# command should be: python manage.py test --keepdb