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
            course_name = form.cleaned_data['course_name']
            course_number = form.cleaned_data['course_number']
            course_url = form.cleaned_data['course_url']
            course_description = form.cleaned_data['course_description']
            course_institution = form.cleaned_data['course_institution']
            c = Course(course_name=course_name, course_number=course_number, course_url=course_url, course_description=course_description, course_institution=course_institution)
            c.save()
            return HttpResponseRedirect(reverse('addCourseList'))
    form = addCourseForm()
    return render(request, 'TransferGuide/addCourseForm.html', {'form': form})


def addCourseList(request):
    allCourseRequests = Course.objects #.order_by('-pub_date')
    return render(request, 'TransferGuide/addCourseList.html', {'allCourseRequests': allCourseRequests.all(), })
