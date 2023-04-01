#models.py

from django.contrib import admin
from django.db import models
from oauth_app.models import UserType
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
class Course(models.Model):
    username = models.ForeignKey(User,on_delete = models.CASCADE)
    course_institution = models.CharField(max_length=100, null=True, blank=True)
    course_name = models.CharField(max_length=100, null=True, blank=True)
    course_dept_num = models.CharField(max_length=100, null=True, blank=True)
    course_grade = models.CharField(max_length=1, null=True, blank=True)
    course_delivery = models.CharField(max_length=10, null=True, blank=True)
    syllabus_url = models.URLField(null=True, blank=True)
    credit_hours = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(10)])
    status = models.CharField(max_length=1,default="P")
    equivalent = models.CharField(max_length=30,default="")
    def __str__(self):
        return str(self.username) + " " + str(self.course_name)

class Viable_Course(models.Model):
    username = models.ForeignKey(User,on_delete = models.CASCADE)
    course_institution = models.CharField(max_length=100, null=True, blank=True)
    course_name = models.CharField(max_length=100, null=True, blank=True)
    course_dept_num = models.CharField(max_length=100, null=True, blank=True)
    course_grade = models.CharField(max_length=1, null=True, blank=True)
    def __str__(self):
        return str(self.username) + " " + str(self.course_name)

class Comment(models.Model):
    title = models.CharField(max_length=200)
    comment_text =models.CharField(max_length=200)
    def __str__(self):
        return self.title + ": " + self.comment_text

