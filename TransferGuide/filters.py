import django_filters
from django_filters import CharFilter
from .models import *


class OrderCourses(django_filters.FilterSet):
    course_institution = CharFilter(field_name="course_institution",lookup_expr="icontains")
    course_name = CharFilter(field_name="course_name",lookup_expr="icontains")


    class Meta:
        model = Course
        fields = '__all__'
        exclude = 'credits, credit_hours,syllabus_url, course_delivery, course_grade, course_dept_num, why_denied, equivalent'