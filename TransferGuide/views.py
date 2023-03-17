from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .forms import addCourseForm 
from .models import Course

def addCourse(request):
    if request.method == 'POST':
        form = addCourseForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                username = request.user.username
                course_institution = form.cleaned_data['course_institution']
                course_name = form.cleaned_data['course_name']
                course_dept = form.cleaned_data['course_dept']
                course_number = form.cleaned_data['course_number']
                course_grade = form.cleaned_data['course_grade']
                course_dept_num = course_dept + " " + course_number
                c = Course(username=username,course_institution=course_institution,course_name=course_name,
                           course_dept_num=course_dept_num,course_grade=course_grade)
                c.save()
            return HttpResponseRedirect(reverse('tryAgain'))
    form = addCourseForm()
    return render(request, 'TransferGuide/addCourseForm.html', {'form': form})


def addCourseList(request):
    allCourseRequests = Course.objects #.order_by('-pub_date')
    return render(request, 'TransferGuide/addCourseList.html', {'allCourseRequests': allCourseRequests.all(), })

def tryAgain(request):
    return render(request, 'TransferGuide/tryAgain.html')