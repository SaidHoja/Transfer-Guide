#forms.py

from django import forms
import datetime
from django.core.exceptions import ValidationError
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
class sisForm(forms.Form):
    subject = forms.CharField(label='Subject (e.g. CS, ASTR, etc.)', max_length=5, required = False)
    term = forms.CharField(max_length=6,widget=forms.Select(choices=[(8, "FALL"), (3, "SPRING")]))

    YEAR_CHOICES = []
    for y in range(2000, (datetime.datetime.now().year + 1)):
        YEAR_CHOICES.append((y, y))
    year= forms.CharField(max_length=4, widget=forms.Select(choices=YEAR_CHOICES))
    instructor = forms.CharField(max_length=20, required = False)

class statusForm(forms.Form):
    status = forms.CharField(label ='Change Status?', max_length=1,widget=forms.Select(choices=[('P','P'),('A','A'),('D','D')]))