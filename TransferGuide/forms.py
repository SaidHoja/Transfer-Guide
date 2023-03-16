#forms.py

from django import forms
 
# creating a form
class addCourseForm(forms.Form):
    course_name = forms.CharField(max_length = 100)
    course_number = forms.CharField(max_length = 100)
    course_url = forms.CharField(max_length = 200)
    course_description = forms.CharField(max_length = 500)
    course_institution = forms.CharField(max_length = 100)

