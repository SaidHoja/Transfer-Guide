#forms.py

from django import forms
 
# creating a form
class addCourseForm(forms.Form):
    course_institution = forms.CharField(max_length=100)
    course_name = forms.CharField(max_length = 100)
    course_dept = forms.CharField(max_length=100)
    course_number = forms.CharField(max_length = 100)
    course_grade = forms.CharField(max_length=1,widget=forms.Select(choices=[('a','A'),('b','B'),('c','C'),('d','D'),('f','F')]))


