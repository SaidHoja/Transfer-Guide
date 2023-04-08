from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import json, requests
from django.core.exceptions import PermissionDenied
from oauth_app.models import UserType
from .forms import requestCourseForm, sisForm, viableCourseFormSet
from .forms import requestCourseForm, sisForm, statusForm, viableCourseForm
from .models import Course, Viable_Course
from .filters import OrderCourses

# Adding Courses by the Student
def requestCourse(request):
    if request.method == 'POST':
        form = requestCourseForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                username = request.user
                course_institution = form.cleaned_data['course_institution']
                course_name = form.cleaned_data['course_name']
                course_dept = form.cleaned_data['course_dept']
                course_number = form.cleaned_data['course_number']
                course_grade = form.cleaned_data['course_grade']
                course_delivery = form.cleaned_data['course_delivery']
                syllabus_url = form.cleaned_data['syllabus_url']
                credit_hours = form.cleaned_data['credit_hours']
                if isRequestNew(username, course_dept, course_number, course_institution):
                    c = Course(username=username,course_institution=course_institution,course_name=course_name,
                           course_dept=course_dept,course_num=course_number,course_grade=course_grade,
                           course_delivery=course_delivery,syllabus_url=syllabus_url,credit_hours=credit_hours)
                    c.save()
            return HttpResponseRedirect(reverse('requestCourseList'))
    form = requestCourseForm()
    return render(request, 'TransferGuide/requestCourseForm.html', {'form': form})
def requestCourseList(request):
    username = request.user
    user_courses = Course.objects.filter(username=username)  # .order_by('-pub_date')
    pending_courses = user_courses.filter(status="P")
    denied_courses = user_courses.filter(status="D")
    approved_courses = user_courses.filter(status="A")
    
    return render(request, 'TransferGuide/requestCourseList.html', {'pending_courses':pending_courses, 'approved_courses':approved_courses, 'denied_courses':denied_courses})

def isRequestNew(username, course_dept, course_num, course_institution):
    user_courses = Course.objects.filter(username=username)
    same_dept = len(user_courses.filter(course_dept=course_dept)) == 0
    same_num = len(user_courses.filter(course_num=course_num)) == 0
    same_institution = len(user_courses.filter(course_institution=course_institution)) == 0
    return same_dept and same_institution and same_num

def submitViableCourse(request):
    formset = viableCourseFormSet()
    if request.method == 'POST':
        formset = viableCourseFormSet(data=request.POST)
        if formset.is_valid():
            for form in formset:
                username = request.user
                course_institution = form.cleaned_data['course_institution']
                course_name = form.cleaned_data['course_name']
                course_dept = form.cleaned_data['course_dept']
                course_number = form.cleaned_data['course_number']
                course_grade = form.cleaned_data['course_grade']
                v = Viable_Course(username=username,course_institution=course_institution,course_name=course_name,
                                  course_dept=course_dept,course_num=course_number,course_grade=course_grade)
                v.save()
            return HttpResponseRedirect(reverse('seeViableCourse'))
    return render(request, 'TransferGuide/viableCourseForm.html', {'viable_course_formset':formset})

def seeViableCourse(request):
    username = request.user
    user_courses = Viable_Course.objects.filter(username=username)
    acceptedCourses = []
    for user_course in user_courses:
        user_dept = user_course.course_dept
        user_num = user_course.course_num
        user_grade = translate_grade(user_course.course_grade)
        matched_courses = Course.objects.filter(course_dept=user_dept)
        matched_courses = matched_courses.filter(course_num=user_num)
        approved_courses = matched_courses.filter(status='A')
        for approved_course in approved_courses:
            if approved_course.status == 'A':
                approved_course_lowest_grade = find_lowest_grade(approved_courses)
                if user_grade >= approved_course_lowest_grade:
                    acceptedCourses.append(user_course)
    return render(request, 'TransferGuide/viableCourseList.html', {'accepted_courses':acceptedCourses})

def translate_grade(grade):
    if grade == 'A':
        return 90
    elif grade == 'B':
        return 80
    elif grade == 'C':
        return 70
    elif grade == 'D':
        return 60
    else:
        return 50

def find_lowest_grade(approved_courses):
    lowest_grade = 100
    for approved_course in approved_courses:
        approved_course_grade = translate_grade(approved_course.course_grade)
        if approved_course_grade < lowest_grade:
            lowest_grade = approved_course_grade
    return lowest_grade

def tryAgain(request):
    return render(request, 'TransferGuide/tryAgain.html')

# Using the SIS API
api_default_url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01"

def SISFormHandler(request):
    form = sisForm()
    if (request.method=="POST"):
        form = sisForm(request.POST)
        if form.is_valid():
            term = "1" + str(form.cleaned_data['year'][-2:]) + str(form.cleaned_data['term'])
            instructor = "None"
            subject = "None"
            if (form.cleaned_data['instructor']!=""):
                instructor = str(form.cleaned_data['instructor'])
            if (form.cleaned_data['subject']!=""):
                subject = str(form.cleaned_data['subject'])

            return redirect('apiResult',term=term,instructor=instructor,subject=subject )
    return render(request,'TransferGuide/sisForm.html', context = {'form':form})

def generateURL(term,instructor,subject):
    url = api_default_url + "&term=" + term
    if (instructor != "None"):
        url += "&instructor=" + instructor
    if (subject != "None"):
        url += "&subject=" + subject
    return url
def apiResult(request, term,instructor, subject):
    url = generateURL(term,instructor,subject)

    result = requests.get(url)
    resultDict = result.json()
    #print(resultDict)
    display = {'headers' : ['acad_group','subject_descr','descr','units'],
              'rows': []}
    i=-1
    rows = []
    for c in resultDict:
        rows.append([])
        i+=1
        for item in display.get('headers'):
            rows[i].append(c[item])
    for elem in rows:
        if (elem not in display.get('rows')):
            display.get('rows').append(elem)
    display['headers']= ['School','Subject', 'Course Title', 'Credits' ]
    return render(request,'TransferGuide/searchResult.html', {'field': display})

def adminApproveCourses(request):
    if (UserType.objects.get(user=request.user).role != "Admin"):
        raise PermissionDenied("Only admin users may access this page.")

    courses = Course.objects.filter()
    coursesFilter = OrderCourses(request.GET, queryset=courses)
    courses = coursesFilter.qs
    return render(request, 'TransferGuide/adminApproval.html', { 'courses': courses, 'coursesFilter': coursesFilter})

def coursePage(request, pk):

    if (UserType.objects.get(user=request.user).role != "Admin"):
        raise PermissionDenied("Only admin users may access this page.")
    form = statusForm()
    course = Course.objects.get(pk=pk)
    if request.method == 'POST':
        form = statusForm(request.POST)
        if form.is_valid():
            course.status=form.cleaned_data['status']
            course.equivalent=form.cleaned_data['equivalent']
            course.why_denied=form.cleaned_data['why_denied']
            course.save()

    return render(request, 'TransferGuide/coursePage.html', {'course': course, 'form':form})
