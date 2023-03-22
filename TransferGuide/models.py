#models.py

from django.contrib import admin
from django.db import models
from oauth_app.models import UserType
from django.contrib.auth.models import User
class Course(models.Model):
    username = models.ForeignKey(User,on_delete = models.CASCADE)
    course_institution = models.CharField(max_length=100, null=True, blank=True)
    course_name = models.CharField(max_length=100, null=True, blank=True)
    course_dept_num = models.CharField(max_length=100, null=True, blank=True)
    course_grade = models.CharField(max_length=1, null=True, blank=True)
    approved = models.CharField(max_length=1,default="P")
    def __str__(self):
        return str(self.username) + " " + str(self.course_name)

class Comment(models.Model):
    title = models.CharField(max_length=200)
    comment_text =models.CharField(max_length=200)
    def __str__(self):
        return self.title + ": " + self.comment_text

