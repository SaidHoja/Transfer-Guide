from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import json, requests
from django.core.exceptions import PermissionDenied
from oauth_app.models import UserType
from .forms import requestCourseForm, sisForm, viableCourseFormSet
from .forms import requestCourseForm, sisForm, statusForm, viableCourseForm, searchCourseForm
from .models import Course, Viable_Course, Request, UserType, User
from .filters import OrderCourses
import re

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
                user_courses = Course.objects.filter(username=username)
                if isRequestNew(user_courses, course_dept, course_number):
                    print("request is made")
                    c = Course(username=username,course_institution=course_institution,course_name=course_name,
                           course_dept=course_dept,course_num=course_number,course_grade=course_grade,
                           course_delivery=course_delivery,syllabus_url=syllabus_url,credit_hours=credit_hours)
                    c.save()
                    r = Request(foreign_course=c, credit_hours=credit_hours)
                    r.save()
            return HttpResponseRedirect(reverse('requestCourseList'))
    form = requestCourseForm()
    return render(request, 'TransferGuide/requestCourseForm.html', {'form': form})
def requestCourseList(request):
    username = request.user
    user_courses = Request.objects.filter(foreign_course__username=username)  # .order_by('-pub_date')
    pending_requests = user_courses.filter(status="P")
    denied_requests = user_courses.filter(status="D")
    approved_requests = user_courses.filter(status="A")
    return render(request, 'TransferGuide/requestCourseList.html', {'pending_requests':pending_requests,
                                                                    'approved_requests':approved_requests,
                                                                    'denied_requests':denied_requests})
# never used but thought might be helpful
def find_courses_from_request(pending_requests):
    courses = []
    for req in pending_requests:
        courses.append(req.foreign_course)
    return courses

def isRequestNew(user_courses, course_dept, course_num):
    requested_courses = Request.objects.filter(foreign_course__course_dept=course_dept)
    requested_courses = requested_courses.filter(foreign_course__course_num=course_num)
    never_checked = len(requested_courses.filter(status='D')) == 0 and len(requested_courses.filter(status='A')) == 0
    course = user_courses.filter(course_dept=course_dept)
    course = course.filter(course_num=course_num)
    diff_course = len(course) == 0
    return diff_course and never_checked

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
    num_of_transfer_courses = 0
    num_of_courses = 0
    username = request.user
    user_courses = Viable_Course.objects.filter(username=username)
    num_of_courses = len(user_courses)
    acceptedCourses = []
    for user_course in user_courses:
        user_grade = translate_grade(user_course.course_grade)
        approved_requests = Request.objects.filter(status='A')
        approved_requests = approved_requests.filter(foreign_course__course_dept=user_course.course_dept)
        # print(user_course.course_dept + str(len(approved_requests)))
        approved_requests = approved_requests.filter(foreign_course__course_num=user_course.course_num)
        # print(str(user_course.course_num) + str(len(approved_requests)))
        approved_courses = find_courses_from_request(approved_requests)
        approved_course_lowest_grade = find_lowest_grade(approved_courses)
        if user_grade >= approved_course_lowest_grade:
            acceptedCourses.append(user_course)
            num_of_transfer_courses += 1
    return render(request, 'TransferGuide/viableCourseList.html', {'accepted_courses':acceptedCourses,
                                                                   'num_of_transfer_courses':num_of_transfer_courses,
                                                                   'num_of_courses':num_of_courses})

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
    requests = []
    for course in courses:
        requests.append(Request.objects.get(foreign_course=course))
    return render(request, 'TransferGuide/adminApproval.html', { 'courses': courses, 'coursesFilter': coursesFilter , 'requests' :requests})

def requestPage(request, pk):

    if (UserType.objects.get(user=request.user).role != "Admin"):
        raise PermissionDenied("Only admin users may access this page.")
    form = statusForm()
    the_request = Request.objects.get(pk=pk)
    course = the_request.foreign_course
    the_request = Request.objects.get(foreign_course__course_name=course.course_name)
    if request.method == 'POST':
        form = statusForm(request.POST)
        if form.is_valid():
            the_request.status=form.cleaned_data['status']
            the_request.uva_course=form.cleaned_data['equivalent'] # this line has gotta go but I don't know how
            the_request.reviewer_comment=form.cleaned_data['reviewer_comment'] # uncomment when field is actually available
            the_request.reviewed_by = request.user
            the_request.save()

    return render(request, 'TransferGuide/requestPage.html', {'course': course, 'form':form})

def searchForCourse(request):
    form = searchCourseForm()
    # select approved courses
    result = Request.objects.filter(status='A')
    if request.method == 'POST':
        form = searchCourseForm(request.POST)
        if form.is_valid():
            institution = form.cleaned_data['institution']
            word = form.cleaned_data['word']
            dept_num = form.cleaned_data['dept_num']
            # print(len(result))
            result = return_transfer_courses(dept_num, institution, result, word)
            # print(len(result))
        return render(request, 'TransferGuide/searchCourseResult.html', {'requests':result})
    return render(request, 'TransferGuide/searchCourse.html', {'form':form})


def return_transfer_courses(dept_num, institution, result, word):
    if institution != "No Preference":
        result = result.filter(foreign_course__course_institution=institution)
    # print(len(result))
    if word != "":
        result = result.filter(foreign_course__course_name__icontains=word)
    # print(len(result))
    if dept_num != "":
        raw_data = dept_num.split()
        dept = raw_data[0]
        num = raw_data[1]
        result = result.filter(uva_course__course_dept__iregex=dept)
        result = result.filter(uva_course__course_num=num)
    return result


def index(request):
    if request.user.is_authenticated:
        username = request.user
        user = UserType.objects.filter(user=username)
        user = user.filter(role='Admin')
        if len(user) == 1:
            own_requests = Request.objects.filter(reviewed_by=username)
            pending_requests = Request.objects.filter(status='P')
            accepted_requests = own_requests.filter(status='A')
            denied_requests = own_requests.filter(status='D')
            return render(request, 'index.html',{'pending_requests': pending_requests, 'accepted_requests': accepted_requests,
                                                'denied_requests': denied_requests})
        else:
            return render(request, 'index.html')
    return render(request, 'index.html')


def allUsers(request):
    if (UserType.objects.get(user=request.user).role != "Admin"):
        raise PermissionDenied("Only admin users may access this page.")

    users = User.objects.all()
    userToType = {}
    for user in users:
        try:
            userToType.update({user: UserType.objects.get(user= user).role})
        except UserType.DoesNotExist:
            userToType.update({user:"None"})

    return render(request,"TransferGuide/userList.html", context = { "userList":userToType })

