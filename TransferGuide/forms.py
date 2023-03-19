#forms.py

from django import forms
 
# creating a form
class addCourseForm(forms.Form):
    course_institution = forms.CharField(max_length=100)
    course_name = forms.CharField(max_length = 100)
    course_dept = forms.CharField(max_length=100)
    course_number = forms.CharField(max_length=10)
    course_grade = forms.CharField(max_length=1,widget=forms.Select(choices=[('A','A'),('B','B'),('C','C'),('D','D'),
                                                                             ('F','F')]))
class sisForm(forms.Form):
    subject = forms.CharField(max_length=10,required = False)
    term = forms.CharField(max_length=6,widget=forms.Select(choices=[(8, "FALL"), (3, "SPRING")]))
    year = forms.IntegerField(max_value=99)
    instructor = forms.CharField(max_length=20, required = False)



