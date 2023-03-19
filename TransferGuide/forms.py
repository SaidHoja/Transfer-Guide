#forms.py

from django import forms
import datetime
 
# creating a form
class addCourseForm(forms.Form):
    course_institution = forms.CharField(max_length=100)
    course_name = forms.CharField(max_length = 100)
    course_dept = forms.CharField(max_length=100)
    course_number = forms.CharField(max_length=10)
    course_grade = forms.CharField(max_length=1,widget=forms.Select(choices=[('A','A'),('B','B'),('C','C'),('D','D'),
                                                                             ('F','F')]))
class sisForm(forms.Form):
    subject = forms.CharField(label='Subject (e.g. CS, ASTR, etc.)', max_length=10, required = False)
    term = forms.CharField(max_length=6,widget=forms.Select(choices=[(8, "FALL"), (3, "SPRING")]))

    YEAR_CHOICES = []
    for y in range(2000, (datetime.datetime.now().year + 1)):
        YEAR_CHOICES.append((y, y))
    year= forms.CharField(max_length=4, widget=forms.Select(choices=YEAR_CHOICES))
    instructor = forms.CharField(max_length=20, required = False)