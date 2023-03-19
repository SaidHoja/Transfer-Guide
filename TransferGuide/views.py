from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import json, requests
from .forms import addCourseForm, sisForm
from .models import Course

# Adding Courses by the Student
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

# Using the SIS API
api_default_url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01"


def SISFormHandler(request):
    form = sisForm()
    if (request.method=="POST"):
        form = sisForm(request.POST)
        if form.is_valid():
            term = "1" + str(form.cleaned_data['year']) + str(form.cleaned_data['term'])
            instructor = "None"
            subject = "None"
            if (form.cleaned_data['instructor']!=""):
                instructor = str(form.cleaned_data['instructor'])
            if (form.cleaned_data['subject']!=""):
                subject = str(form.cleaned_data['subject'])

            return redirect('apiResult',term=term,instructor=instructor,subject=subject )
    return render(request,'TransferGuide/sisForm.html', context = {'form':form})

def apiResult(request, term,instructor, subject):
    url = api_default_url + "&term=" + term
    if (instructor!="None"):
        url+= "&instructor=" + instructor
    if (subject!="None"):
        url+= "&subject=" +subject
    print(url)
    result = requests.get(url)
    resultDict = result.json()
    textDict = {'a': [ [1, 2] ], 'b': [ [3, 4] ],'c':[ [5,6]] }
    return render(request,'TransferGuide/searchResult.html', {'renderdict': textDict})

