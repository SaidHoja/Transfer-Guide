#models.py

from django.contrib import admin
from django.db import models

class Course(models.Model):
    course_name = models.CharField(max_length = 100)
    course_number = models.CharField(max_length = 100)
    course_url = models.CharField(max_length = 200)
    course_description = models.CharField(max_length = 500)
    course_institution = models.CharField(max_length = 100)
    def __str__(self):
        return self.course_name
        return self.course_number
        return self.course_url
        return self.course_description
        return self.course_institution

class Comment(models.Model):
    title = models.CharField(max_length=200)
    comment_text =models.CharField(max_length=200)
    def __str__(self):
        return self.title + ": " + self.comment_text

