#forms.py

from django import forms
from django.forms.formsets import formset_factory
import datetime
from django.core.exceptions import ValidationError
from .models import Viable_Course, Course, Request, UVA_Course
from django.db.models.signals import pre_save
from django.dispatch import receiver
# creating a form

def validate_one_word(value):
    if len(value.split()) != 1:
        raise ValidationError("Please enter only one word.")
class requestCourseForm(forms.Form):
    course_institution = forms.CharField(max_length=100)
    course_name = forms.CharField(max_length = 100)
    course_dept = forms.CharField(max_length=5, validators=[validate_one_word])
    course_number = forms.IntegerField(min_value=0, max_value=9999)
    course_grade = forms.CharField(max_length=1,widget=forms.Select(choices=[('A','A'),('B','B'),('C','C'),('D','D'),
                                                                             ('F','F')]))
    course_delivery = forms.CharField(max_length=10, widget=forms.Select(choices=[('IN-PERSON','IN-PERSON'), (
        'ONLINE','ONLINE')]))
    syllabus_url = forms.URLField()
    credit_hours = forms.IntegerField(min_value=0, max_value=10)

class viableCourseForm(forms.Form):
    course_institution = forms.CharField(max_length=100)
    course_name = forms.CharField(max_length = 100)
    course_dept = forms.CharField(max_length=6, validators=[validate_one_word])
    course_number = forms.IntegerField(min_value=0, max_value=9999)
    course_grade = forms.CharField(max_length=1,widget=forms.Select(choices=[('A','A'),('B','B'),('C','C'),('D','D'),
                                                                             ('F','F')]))

viableCourseFormSet = formset_factory(viableCourseForm, extra=1)
class sisForm(forms.Form):
    subject = forms.CharField(label='Subject (e.g. CS, ASTR, etc.)', max_length=5, required = False)
    term = forms.CharField(max_length=6,widget=forms.Select(choices=[(8, "FALL"), (3, "SPRING")]))

    YEAR_CHOICES = []
    for y in range(2000, (datetime.datetime.now().year + 1)):
        YEAR_CHOICES.append((y, y))
    year= forms.CharField(max_length=4, widget=forms.Select(choices=YEAR_CHOICES))
    instructor = forms.CharField(max_length=20, required = False)

class statusForm(forms.Form):
    status = forms.CharField(label ='Change Status?', max_length=1,widget=forms.Select(choices=[('P','Pending'),('A','Approve'),('D','Deny')]))
    equivalent = forms.CharField(label='Equivalent UVA Course', max_length=30, required = False, help_text="Only fill out if approved.")
    why_denied = forms.CharField(label="Reason for Denying Approval", max_length=200, required=False, help_text="Only fill out if denied.")
#    def equivalent_course(self):
 #       if self.cleaned_data.get('status', None) == 'A':
 #           if self.cleaned_data.get('equivalent', None) is not None:
 #               pass

def institution_as_widget():
    # only select courses that have been approved by staff
    set_of_institutes = set()
    for request in Request.objects.all():
        course = request.foreign_course
        set_of_institutes.add(course.course_institution)
    result = []
    result.append(("No Preference", "No Preference"))
    for institute in set_of_institutes:
        result.append((institute, institute))
    return result

def mnemonic_as_widget():
    # only select courses that have been approved by staff
    set_of_mnemonics = set()
    for course in UVA_Course.objects.all():
        set_of_mnemonics.add(course.course_dept)
    result = []
    result.append(("No Preference", "No Preference"))
    for mnemonic in set_of_mnemonics:
        result.append((mnemonic, mnemonic))
    return result

def validate_dept_num(value):
    raw_values = value.split()
    if len(raw_values) != 2 and len(raw_values) != 0:
        raise ValidationError("Enter only a department (e.g. CS) and course number (3240)")
    else:
        if not raw_values[0].isalpha():
            raise ValidationError("Enter only letters in the department (e.g. CS)")
        if raw_values[1].isnumeric():
           if int(raw_values[1]) < 1000:
               raise ValidationError("Enter a valid UVA course number (> 1000)")
        else:
            raise ValidationError("Enter a valid number for the course number")

class searchCourseForm(forms.Form):
    institution = forms.CharField(label='Select an institution to transfer courses from', max_length=100,
                                  widget=forms.Select(choices=institution_as_widget()))
    word = forms.CharField(label='Look for all classes that share this word. (e.g. Enter "anthropology" to look for Anthropology of Water',
                           max_length=100, required=False)
    dept_num = forms.CharField(label='Input a UVA course department and number to see all transferable courses',
                                max_length=13, validators=[validate_dept_num], required=False)
    # def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        #     self.fields['course_name'] = forms.CharField(max_length=50, required=True)
    # def clean(self):
    #     course_set = set()
    #     result_list = []
    #     if self.cleaned_data['mnemonic'] != "No Preference":
    #         uva_courses = UVA_Course.objects.all()
    #         for course in uva_courses:
    #             if course.course_dept == self.cleaned_data['mnemonic']:
    #                 course_name = course.course_dept + " " + str(course.course_num) + ": " + str(course.course_name)
    #                 course_set.add(course_name)
    #         for course_name in course_set:
    #             result_list.append((course_name, course_name))
    #         self.fields['course_name'] = forms.CharField(label='Select a course name you want to search for',
    #                                                       max_length=100, widget=forms.Select(choices=result_list))
    #         print(True)
