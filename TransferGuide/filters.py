import django_filters
from django_filters import *
from .models import *
from django.core.exceptions import ValidationError


class OrderCourses(django_filters.FilterSet):
    course_institution = CharFilter(label = "Course Institution" , field_name="course_institution",lookup_expr="icontains")
    course_dept = CharFilter(label = "Course Department", field_name = "course_dept", lookup_expr="icontains")
    course_num = NumberFilter(label = "Course Number", field_name = "course_num",lookup_expr="exact" )
    course_name = CharFilter(label = "Course Title" ,field_name="course_name",lookup_expr="icontains")
    username = ModelChoiceFilter(queryset=User.objects.all(), label = "Submitted By")

    class Meta:
        model = Course
        fields = '__all__'
        exclude = 'username ,course_institution,course_name, course_dept ,course_num ,course_grade,course_delivery,syllabus_url,credit_hours'
