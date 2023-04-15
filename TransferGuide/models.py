#models.py

from django.contrib import admin
from django.db import models
from oauth_app.models import UserType
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
class Course(models.Model):
    username = models.ForeignKey(User,on_delete = models.CASCADE)
    course_institution = models.CharField(max_length=100, null=False, blank=True)
    course_name = models.CharField(max_length=100, null=False, blank=True)
    course_dept = models.CharField(max_length=100, null = True)
    course_num = models.PositiveIntegerField(null= True, validators=[MinValueValidator(1)]);
    course_grade = models.CharField(max_length=1, null=False, blank=True)
    course_delivery = models.CharField(max_length=10, null=False, blank=True)
    syllabus_url = models.URLField(null=True, blank=True)
    credit_hours = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(10)])
    def __str__(self):
        return str(self.username) + " " + str(self.course_name)

class UVA_Course(models.Model):
    course_name = models.CharField(max_length=100, null = False)
    course_dept = models.CharField(max_length=100, null = False)
    course_num = models.PositiveIntegerField(null=False)
    credit_hours = models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(10)])

    def __str__(self):
        return self.course_dept + " " + str(self.course_num) + " " + self.course_name
class Request(models.Model):
    uva_course = models.ForeignKey(UVA_Course,null = True, on_delete=models.CASCADE);
    foreign_course = models.ForeignKey(Course, null = False, on_delete=models.CASCADE)
    status = models.CharField(max_length = 1, default = "P", choices = [("A","A"),("D","D"),("P","P")])
    credit_hours =  models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(10)], null = True)
    reviewed_by = models.ForeignKey(User,null=True, on_delete=models.CASCADE)

class Viable_Course(models.Model):
    username = models.ForeignKey(User,on_delete = models.CASCADE)
    course_institution = models.CharField(max_length=100, null=True, blank=True)
    course_name = models.CharField(max_length=100, null=True, blank=True)
    course_dept = models.CharField(max_length=100, null=True, blank=True)
    course_num = models.PositiveIntegerField(null = True)
    course_grade = models.CharField(max_length=1, null=True, blank=True)
    def __str__(self):
        return str(self.username) + " " + str(self.course_name)

class Comment(models.Model):
    title = models.CharField(max_length=200)
    comment_text =models.CharField(max_length=200)
    def __str__(self):
        return self.title + ": " + self.comment_text

