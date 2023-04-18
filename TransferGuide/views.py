from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import json, requests
from django.core.exceptions import PermissionDenied, ValidationError
from oauth_app.models import UserType
from .forms import requestCourseForm, sisForm, viableCourseFormSet
from .forms import requestCourseForm, sisForm, statusForm, viableCourseForm, searchCourseForm, editRoleForm, KnownTransferForm
from .models import Course, Viable_Course, Request, UserType, User
from .filters import OrderCourses
import re
from django.db.models import Q

# Adding Courses by the Student
def requestCourse(request):
    if request.method == 'POST':
        form = requestCourseForm(request.POST)
        try:
            if form.is_valid():
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
                # print(wasCourseApproved(course_dept, course_number, course_institution))
                # print(wasCourseDenied(course_dept, course_number, course_institution))
                if wasCourseApproved(course_dept, course_number, course_institution):
                    if translate_grade(course_grade) >= 70:
                        raise ValidationError("This course has already been marked as pre-approved. Your score is high enough to transfer.")
                    else:
                        raise ValidationError("This course has already been marked as pre-approved. Your score is too low to transfer.")
                elif wasCourseDenied(course_dept, course_number, course_institution):
                    # print("course denied")
                    if deniedDueToLowGrade(course_dept, course_number, course_institution):
                        # print("denied due to low grade")
                        if translate_grade(course_grade) >= 70:
                            raise ValidationError("This course has been reviewed. Your grade is high enough for your credit to transfer")
                        else:
                            raise ValidationError("This course has been reviewed. Your grade is too low for your credit to transfer.")
                    else:
                        raise ValidationError("This course was never approved because it did not align with UVA's high expectations for education.")
                elif doesCourseExist(user_courses, course_dept, course_number, course_institution):
                    c = Course(
                        username=username,
                        course_institution=course_institution,
                        course_name=course_name,
                        course_dept=course_dept,
                        course_num=course_number,
                        course_grade=course_grade,
                        course_delivery=course_delivery,
                        syllabus_url=syllabus_url,
                        credit_hours=credit_hours
                    )
                    c.save()
                    r = Request(foreign_course=c, credit_hours=credit_hours)
                    r.save()
                    return HttpResponseRedirect(reverse('requestCourseList'))
        except ValidationError as e:
            return render(request, 'TransferGuide/requestCourseForm.html', {'form': form, 'error': e})
    form = requestCourseForm()
    return render(request, 'TransferGuide/requestCourseForm.html', {'form': form})
def requestCourseList(request):
    username = request.user
    user_courses = Request.objects.filter(foreign_course__username=username)  # .order_by('-pub_date')
    pending_requests = user_courses.filter(status="P")
    denied_requests = user_courses.filter(Q(status="D_LowGrade") | Q(status="D_BadFit"))
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

def doesCourseExist(user_courses, course_dept, course_num, course_institution):
    course = user_courses.filter(course_dept__iexact=course_dept)
    course = course.filter(course_num=course_num)
    course = course.filter(course_institution__iexact=course_institution)
    never_submitted = len(course) == 0
    return never_submitted

def wasCourseApproved(course_dept, course_num, course_institution):
    requested_courses = Request.objects.filter(foreign_course__course_dept__iexact=course_dept)
    requested_courses = requested_courses.filter(foreign_course__course_num=course_num)
    requested_courses = requested_courses.filter(foreign_course__course_institution__iexact=course_institution)
    was_approved = len(requested_courses.filter(status='A')) >= 1
    return was_approved

def wasCourseDenied(course_dept, course_num, course_institution):
    requested_courses = Request.objects.filter(foreign_course__course_dept__iexact=course_dept)
    requested_courses = requested_courses.filter(foreign_course__course_num=course_num)
    requested_courses = requested_courses.filter(foreign_course__course_institution__iexact=course_institution)
    was_denied = len(requested_courses.filter(Q(status='D_LowGrade') | Q(status='D_BadFit'))) >= 1
    return was_denied

def deniedDueToLowGrade(course_dept, course_num, course_institution):
    requested_courses = Request.objects.filter(foreign_course__course_dept__iexact=course_dept)
    requested_courses = requested_courses.filter(foreign_course__course_num=course_num)
    requested_courses = requested_courses.filter(foreign_course__course_institution__iexact=course_institution)
    requested_courses = requested_courses.filter(status="D_LowGrade")
    return len(requested_courses) > 0
def getTransferCourse(course_dept, course_num, course_institution):
    courses = Course.objects.filter(course_dept__iexact=course_dept)
    courses = courses.filter(course_num=course_num)
    courses = courses.filter(course_institution__iexact=course_institution)
    return courses.first()

def getUVACourse(course_dept, course_num, course_institution):
    requested_courses = Request.objects.filter(foreign_course__course_dept__iexact=course_dept)
    requested_courses = requested_courses.filter(foreign_course__course_num=course_num)
    requested_courses = requested_courses.filter(foreign_course__course_institution__iexact=course_institution)
    first_request = requested_courses.first()
    return first_request.uva_course

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
                # error checking
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
    approved_requests = Request.objects.filter(Q(status='A') | Q(status='D_LowGrade'))
    print(len(approved_requests))
    acceptedCourses = []
    for user_course in user_courses:
        user_grade = translate_grade(user_course.course_grade)
        specific_requests = approved_requests.filter(foreign_course__course_institution__iexact=user_course.course_institution)
        specific_requests = specific_requests.filter(foreign_course__course_dept__iexact=user_course.course_dept)
        specific_requests = specific_requests.filter(foreign_course__course_num=user_course.course_num)
        approved_course_lowest_grade = 70
        if len(specific_requests) > 0:
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
    requests = Request.objects.filter(Q(status='A') | Q(status='D_LowGrade'))
    if request.method == 'POST':
        form = searchCourseForm(request.POST)
        if form.is_valid():
            institution = form.cleaned_data['institution']
            word = form.cleaned_data['word']
            dept_num = form.cleaned_data['dept_num']
            # print(len(result))
            result = return_transfer_courses(dept_num, institution, requests, word)
            # print(len(result))
        return render(request, 'TransferGuide/searchCourseResult.html', {'requests':result})
    return render(request, 'TransferGuide/searchCourse.html', {'form':form})


def return_transfer_courses(dept_num, institution, result, word):
    if institution != "No Preference":
        result = result.filter(foreign_course__course_institution__icontains=institution)
    # print(len(result))
    if word != "":
        result = result.filter(foreign_course__course_name__icontains=word)
    print(result.last().uva_course.course_dept)
    print(len(result))
    if dept_num != "":
        raw_data = dept_num.split()
        if len(raw_data) >= 1:
            dept = raw_data[0]
            result = result.filter(uva_course__course_dept__iexact=dept)
            print(len(result))
        if len(raw_data) >= 2:
            num = raw_data[1]
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
            denied_requests = own_requests.filter(Q(status='D_BadFit') | Q(status='D_LowGrade'))
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
    userForm = editRoleForm()
    if (request.method == "POST"):
        userForm = editRoleForm(request.POST)
        print("yes1")
        if (userForm.is_valid()):
            print("yes2")
            try:
                userToChange = User.objects.get(username = userForm.cleaned_data["user"])
                userTypeToChange = UserType.objects.get(user = userToChange)
                userTypeToChange.role = userForm.cleaned_data["newUserRole"]
                print(userForm.cleaned_data["newUserRole"])
                userTypeToChange.save()
                print("yes3")
            except UserType.DoesNotExist:
                newUserType = UserType(user = User.objects.get(username=userForm.cleaned_data["user"]), role = userForm.cleaned_data["newUserRole"])
                newUserType.save()
                print("yes4")


    for user in users:
        try:
            userToType.update({user: UserType.objects.get(user= user).role})
        except UserType.DoesNotExist:
            userToType.update({user:"None"})

    return render(request,"TransferGuide/userList.html", context = { "userList":userToType , "form" : userForm })

def addKnownTransfer(request):
    if (UserType.objects.get(user=request.user).role != "Admin"):
        raise PermissionDenied("Only admin users may access this page.")
    form = KnownTransferForm()

    if (request.method == "POST"):
        form = KnownTransferForm(request.POST)
        if (form.is_valid()):
            the_request = Request()
            new_course = Course()
            new_course.username = request.user
            new_course.course_institution = form.cleaned_data['course_institution']
            new_course.course_name = form.cleaned_data['course_name']
            new_course.course_dept = form.cleaned_data['course_dept']
            new_course.course_number = form.cleaned_data['course_number']
            new_course.course_grade = form.cleaned_data['course_grade']
            new_course.course_delivery = form.cleaned_data['course_delivery']
            new_course.syllabus_url = form.cleaned_data['syllabus_url']
            new_course.credit_hours = form.cleaned_data['credit_hours']
            new_course.save()
            the_request.foreign_course = new_course
            the_request.status = form.cleaned_data['status']
            the_request.uva_course = form.cleaned_data['equivalent']
            the_request.reviewer_comment = form.cleaned_data['reviewer_comment']
            the_request.save()

    return render(request, "TransferGuide/knownTransferForm.html", {"form":form})

