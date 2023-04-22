#forms.py

from django import forms
from django.forms.formsets import formset_factory
import datetime
from django.core.exceptions import ValidationError
from .models import Viable_Course, Course, Request, UVA_Course, UserType, User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Q
# creating a form

def validate_one_word(value):
    if len(value.split()) != 1:
        raise ValidationError("Please enter only one word.")
    if not value.isalpha():
        raise ValidationError("Please enter a valid word. Uses characters A-Z")

def validate_non_uva(value):
    if value.lower() == "university of virginia":
        raise ValidationError("Please enter a non-UVA course.")
class requestCourseForm(forms.Form):
    course_institution = forms.CharField(max_length=100, validators=[validate_non_uva],
                                         widget=forms.TextInput(attrs={'placeholder': 'Enter the instutition your course is from.'}))
    course_name = forms.CharField(max_length = 100, widget=forms.TextInput(attrs={'placeholder': 'Enter the name of your course'}))
    course_dept = forms.CharField(max_length=5, validators=[validate_one_word], widget=forms.TextInput(attrs={'placeholder': 'Example: enter MATH for transfer course MATH 1000'}))
    course_number = forms.IntegerField(min_value=0, max_value=9999)
    course_grade = forms.CharField(max_length=1,widget=forms.Select(choices=[('A','A'),('B','B'),('C','C'),('D','D'),
                                                                             ('F','F')]))
    course_delivery = forms.CharField(max_length=10, widget=forms.Select(choices=[('IN-PERSON','IN-PERSON'), (
        'ONLINE','ONLINE')]))
    syllabus_url = forms.URLField(widget=forms.TextInput(attrs={'placeholder': 'Enter homepage of course or link to syllabus.'}))
    credit_hours = forms.IntegerField(min_value=0, max_value=10)

class viableCourseForm(forms.Form):
    course_institution = forms.CharField(max_length=100, validators=[validate_non_uva],
                                         widget=forms.TextInput(attrs={'placeholder': 'Enter the institution your course came from.'}))
    course_name = forms.CharField(max_length=100,
                                  widget=forms.TextInput(attrs={'placeholder': 'Enter the name of your course'}))
    course_dept = forms.CharField(max_length=6, validators=[validate_one_word],
                                  widget=forms.TextInput(attrs={'placeholder': 'Enter "CS", "ENGL", "APMA", "CHEM".'}))
    course_number = forms.IntegerField(min_value=0, max_value=9999)
    course_grade = forms.CharField(max_length=1,widget=forms.Select(choices=[('A','A'),('B','B'),('C','C'),('D','D'),
                                                                             ('F','F')]))

viableCourseFormSet = formset_factory(viableCourseForm, extra=1)
class sisForm(forms.Form):
    subject = forms.CharField(label='Subject', max_length=5, required = False,
                              widget=forms.TextInput(attrs={'placeholder': 'Enter "CS", "ENGL", "APMA", "CHEM".'}),
                              validators=[validate_one_word])
    term = forms.CharField(max_length=6,widget=forms.Select(choices=[(8, "FALL"), (3, "SPRING")]))
    YEAR_CHOICES = []
    for y in range(2000, (datetime.datetime.now().year + 1)):
        YEAR_CHOICES.append((y, y))
    year= forms.CharField(max_length=4, widget=forms.Select(choices=YEAR_CHOICES))
    instructor = forms.CharField(max_length=20, required = False,
                                 widget=forms.TextInput(attrs={'placeholder': 'Enter last name of instructor.'}))

class approveForm(forms.Form):
    credits_approved = forms.IntegerField(label = "Approve for how many credits?", min_value = 0, required=True)
    equivalent = forms.ModelChoiceField(queryset = UVA_Course.objects.all(), label='Equivalent UVA Course', required = True, help_text="Only fill out if approved.")
    reviewer_comment = forms.CharField(label="Reviewer Comment", max_length=200, required=False)


class statusForm(forms.Form):
 #   credits_approved = forms.IntegerField(label = "Approve for how many credits?", min_value = 0, required=False)
    status = forms.CharField(label ='Change Status?',required= True ,max_length=20,widget=forms.Select(choices=[('P','Pending'),('A','Approve'),
                                                                                                ('D_LowGrade','Deny due to low grade'),
                                                                                                ('D_BadFit', 'Deny due to course misalignment')]))
 #   equivalent = forms.ModelChoiceField(queryset = UVA_Course.objects.all(), label='Equivalent UVA Course', required = False, help_text="Only fill out if approved.")
 #   reviewer_comment = forms.CharField(label="Reviewer Comment", max_length=200, required=False)
    def clean(self):
        i=1
  #      if self.cleaned_data.get('status') == 'A': # make sure equivalent course is provided when approved
   #         if self.cleaned_data.get('equivalent') is None:
    #            msg = forms.ValidationError("This field is required for approved courses.")
     #           self.add_error('equivalent', msg)
      #      if self.cleaned_data.get('credits_approved') is None:
       #         msg = forms.ValidationError("This field is required for approved courses.")
        #        self.add_error('credits_approved', msg)

        # if self.cleaned_data.get('status') == 'D_LowGrade': # set default comments
        #     if not self['reviewer_comment']:
        #         self['reviewer_comment'] = "Grade is too low"
        # if self.cleaned_data.get('status') == 'D_BadFit':
        #     if not self['reviewer_comment']:
        #         self['reviewer_comment'] = "Course does not meet standards"
            

def institution_as_widget():
    # only select courses that have been approved by staff
    set_of_institutes = set()
    for request in Request.objects.filter(Q(status='A') | Q(status='D_LowGrade')):
        course = request.foreign_course
        set_of_institutes.add(course.course_institution)
    result = []
    result.append(("No Preference", "No Preference"))
    for institute in set_of_institutes:
        result.append((institute, institute))
    result = sorted(result, key=lambda x: (x[0] != 'No Preference', x))
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
    if len(raw_values) > 2:
        raise ValidationError("You can enter a department (e.g. CS) and course number (3240), only a department (e.g. CS), or leave this field blank.")
    else:
        if len(raw_values) >= 1:
            if not raw_values[0].isalpha():
                raise ValidationError("Enter only letters in the department (e.g. CS)")
        if len(raw_values) >= 2:
            if raw_values[1].isnumeric():
               if int(raw_values[1]) < 1000:
                   raise ValidationError("Enter a valid UVA course number (> 1,000)")
               elif int(raw_values[1]) > 9999:
                   raise ValidationError("Enter a valid UVA course number (< 10,000)")
            else:
                raise ValidationError("Enter a valid number for the course number")

class searchCourseForm(forms.Form):
    institution = forms.CharField(label='Select an institution to transfer courses from', max_length=100,
                                  widget=forms.Select(choices=institution_as_widget()), required=False)
    word = forms.CharField(label='Look for all classes that share this word.',
                           widget=forms.TextInput(attrs={'placeholder': 'Enter "astrophysics" to see the Dartmouth\'s Introduction to Astrophysics.'}),
                           max_length=100, required=False)
    dept_num = forms.CharField(label='Input a UVA course department and number to see all transferable courses',
                               widget=forms.TextInput(attrs={'placeholder': 'Enter "APMA 2120" to see all courses that transfer to UVA\'s Calc 2 Class. Enter "APMA" to see all courses that transfer to UVA\'s APMA department'}),
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

class editRoleForm(forms.Form):
    newUserRole = forms.CharField(label = "Change role" ,widget=forms.Select(choices=[("Student", "Student"), ["Admin","Admin"]]))
    user = forms.CharField(widget= forms.HiddenInput())

class KnownTransferForm(forms.Form):
    course_institution = forms.CharField(max_length=100, required = True)
    course_name = forms.CharField(max_length = 100, required = True)
    course_dept = forms.CharField(max_length=5, validators=[validate_one_word], required = True)
    course_number = forms.IntegerField(min_value=0, max_value=9999, required = True)
    status = forms.CharField(label ='Denied or Approved?',required = True, max_length=20,widget=forms.Select(choices=[('A','Approve'),
                                                                                                      ('D_LowGrade','Deny due to Low Grade'),
                                                                                                      ('D_BadFit', 'Deny due to course misalignment')]))
    course_grade = forms.CharField(label = "Minimum grade", max_length=1,widget=forms.Select(choices=[('A','A'),('B','B'),('C','C'),('D','D'),
                                                                             ('F','F')]))
    course_delivery = forms.CharField(max_length=10, widget=forms.Select(choices=[('IN-PERSON','IN-PERSON'), (
        'ONLINE','ONLINE')]))
    syllabus_url = forms.URLField()
    credit_hours = forms.IntegerField(min_value=0, max_value=10)
    credits_approved = forms.IntegerField(label = "Approve for how many credits?", )

    equivalent = forms.ModelChoiceField(queryset = UVA_Course.objects.all(), label='Equivalent UVA Course', required = False, help_text="Only fill out if approved.")
    reviewer_comment = forms.CharField(label="Review Comment", max_length=200, required=False, help_text="Must fill out if denied.")