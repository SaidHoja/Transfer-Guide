from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
import json, requests
from django.core.exceptions import PermissionDenied, ValidationError
from oauth_app.models import UserType
from .forms import requestCourseForm, sisForm, viableCourseFormSet
from .forms import *
from .models import Course, Viable_Course, Request, UserType, User
from .filters import OrderCourses
import re
from django.db.models import Q, F
# from fuzzywuzzy import fuzz

# Adding Courses by the Student
def requestCourse(request):
    error = ""
    if request.method == 'POST':
        form = requestCourseForm(request.POST)
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

            if course_institution.upper() == "UNIVERSITY OF VIRGINIA":
                error = "You cannot submit a UVA-taught course as a transfer course"
                return render(request, 'TransferGuide/requestCourseForm.html', {'form': form, "error": error})
            error = course_name_has_error(course_institution, course_name, course_dept, course_number)
            if error != "":
                return render(request, 'TransferGuide/requestCourseForm.html', {'form': form, "error":error})
            error = credit_hour_has_erorr(course_institution, course_dept, course_number, credit_hours)
            if error != "":
                return render(request, 'TransferGuide/requestCourseForm.html', {'form': form, "error": error})
            if userSubmittedCourse(username, course_dept, course_number, course_institution):
                user_request = getUserRequest(username, course_dept, course_number, course_institution)
                print(user_request)
                if user_request.status == 'A':
                    if translate_grade(course_grade) < 70:
                        user_request.status = 'D_LowGrade'
                elif user_request.status == 'D_LowGrade':
                    if translate_grade(course_grade) >= 70:
                        user_request.status = 'A'
                user_request.save()
                # return render(request, 'TransferGuide/requestCourseForm.html', {'form': form, 'error': error})
            else:
                c = Course(username=username, course_institution=course_institution, course_name=course_name, course_dept=course_dept,
                    course_num=course_number, course_grade=course_grade, course_delivery=course_delivery, syllabus_url=syllabus_url,
                    credit_hours=credit_hours)
                c.save()
                if wasCourseApproved(course_dept, course_number, course_institution):
                    uva_course = getUVACourse(course_dept, course_number, course_institution)
                    if translate_grade(course_grade) >= 70:
                        r = Request(uva_course=uva_course, foreign_course=c, status='A', credit_hours=credit_hours,
                                    reviewer_comment="Autoapproved - grade is sufficient")
                        r.save()
                    else:
                        r = Request(uva_course=uva_course, foreign_course=c, status='D_LowGrade', credit_hours=credit_hours,
                                    reviewer_comment="Autodeclined - grade is too low")
                        r.save()
                elif wasCourseDenied(course_dept, course_number, course_institution):
                    if deniedDueToLowGrade(course_dept, course_number, course_institution):
                        if translate_grade(course_grade) >= 70:
                            r = Request(foreign_course=c, status='P', credit_hours=credit_hours,
                                        reviewer_comment="Credit should be approved but waiting for reviewer to assign equivalent UVA course")
                            r.save()
                        else:
                            r = Request(foreign_course=c, status='D_LowGrade', credit_hours=credit_hours,
                                        reviewer_comment="Autodeclined - grade is too low")
                            r.save()
                    else:
                        r = Request(foreign_course=c, status='D_BadFit', credit_hours=credit_hours,
                                    reviewer_comment="Autodeclined - course does not align with UVA's educational values")
                        r.save()
                else:
                    r = Request(foreign_course=c, credit_hours=credit_hours)
                    r.save()
            messages.success(request, "Course successfully submitted!")
            return HttpResponseRedirect('/')
    form = requestCourseForm()
    return render(request, 'TransferGuide/requestCourseForm.html', {'form': form})
def requestCourseList(request):
    username = request.user
    user_courses = Request.objects.filter(foreign_course__username=username)  # .order_by('-pub_date')
    pending_requests = user_courses.filter(status="P")
    denied_requests = user_courses.filter(Q(status="D_LowGrade") | Q(status="D_BadFit"))
    print(len(denied_requests))
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

def userSubmittedCourse(username, course_dept, course_num, course_institution):
    user_courses = Course.objects.filter(Q(username=username) & Q(course_dept__iexact=course_dept) &
                                         Q(course_num=course_num) & Q(course_institution__iexact=course_institution))
    return len(user_courses) > 0

def getUserRequest(username, course_dept, course_num, course_institution):
    user_request = Request.objects.filter(Q(foreign_course__username=username) & Q(foreign_course__course_dept__iexact=course_dept),
                                          Q(foreign_course__course_num=course_num) &
                                          Q(foreign_course__course_institution__iexact=course_institution))
    return user_request.first()

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
    num_of_courses = 0
    num_of_transfer_courses = 0
    approved_requests = Request.objects.filter(Q(status='A'))
    accepted_courses = {}
    error = ""
    if request.method == 'POST':
        formset = viableCourseFormSet(data=request.POST)
        if formset.is_valid():
            list_of_courses = []
            for form in formset:
                course_institution = form.cleaned_data['course_institution']
                course_name = form.cleaned_data['course_name']
                course_dept = form.cleaned_data['course_dept']
                course_number = form.cleaned_data['course_number']
                query = course_institution + " " + course_dept + " " + str(course_number)
                if query not in list_of_courses:
                    list_of_courses.append(query)
                else:
                    error = "At least two of the courses you inputted are duplicates. Please try again"
                    return render(request, 'TransferGuide/viableCourseForm.html', {'viable_course_formset': formset,
                                                                                   'error':error})
                error = course_name_has_error(course_institution, course_name, course_dept, course_number)
                if error != "":
                    return render(request, 'TransferGuide/viableCourseForm.html', {'viable_course_formset': formset,
                                                                                   'error': error})
            for form in formset:
                course_institution = form.cleaned_data['course_institution']
                course_name = form.cleaned_data['course_name']
                course_dept = form.cleaned_data['course_dept']
                course_number = form.cleaned_data['course_number']
                course_grade = form.cleaned_data['course_grade']
                num_of_courses += 1
                specific_requests = approved_requests.filter(foreign_course__course_institution__iexact=course_institution)
                specific_requests = specific_requests.filter(foreign_course__course_dept__iexact=course_dept)
                specific_requests = specific_requests.filter(foreign_course__course_num=course_number)
                approved_course_lowest_grade = 70
                if len(specific_requests) > 0:
                    print(specific_requests.first())
                    uva_course = specific_requests.first().uva_course
                    if translate_grade(course_grade) >= approved_course_lowest_grade:
                        num_of_transfer_courses += 1
                        new_course = {num_of_transfer_courses: {'transfer_course_institution': course_institution,
                                                                'transfer_course_name': course_name,
                                                                'transfer_course_dept': course_dept,
                                                                'transfer_course_num': course_number,
                                                                'uva_course_name':uva_course.course_name,
                                                                'uva_course_dept':uva_course.course_dept,
                                                                'uva_course_num':uva_course.course_num}}
                        accepted_courses.update(new_course)
            return render(request, 'TransferGuide/viableCourseList.html', {'accepted_courses': accepted_courses,
                                                                           'num_of_transfer_courses': num_of_transfer_courses,
                                                                           'num_of_courses': num_of_courses})
    return render(request, 'TransferGuide/viableCourseForm.html', {'viable_course_formset':formset})

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

def course_name_has_error(course_institution, course_name, course_dept, course_num):
    set_of_courses = Course.objects.filter(Q(course_institution__iexact=course_institution) &
                                           Q(course_dept__iexact=course_dept) & Q(course_num=course_num))
    error = ""
    if len(set_of_courses) > 0:
        course = set_of_courses.first()
        if course.course_name.lower() != course_name.lower():
            error = "It seems the course " + course_dept + " " + str(course_num) + " at " + course_institution +\
                    " exists but the course name you entered is wrong. Did you mean to enter: " + course.course_name + \
                    ", as the course name?"
    return error

def credit_hour_has_erorr(course_institution, course_dept, course_num, credit_hours):
    set_of_courses = Course.objects.filter(Q(course_institution__iexact=course_institution) &
                                           Q(course_dept__iexact=course_dept) & Q(course_num=course_num))
    error = ""
    if len(set_of_courses) > 0:
        course = set_of_courses.first()
        if course.credit_hours != credit_hours:
            error = "It seems the course " + str(course_dept) + " " + str(course_num) + " at " + course_institution + \
                    " exists but the number of credit hours you entered is wrong. Did you mean to enter: " + \
                    str(course.credit_hours) + ", as the number of credit hours"
    return error

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
            page = 1
            if (form.cleaned_data['instructor']!=""):
                instructor = str(form.cleaned_data['instructor'])
            if (form.cleaned_data['subject']!=""):
                subject = str(form.cleaned_data['subject']).upper()

            return redirect('apiResult',term=term,instructor=instructor,subject=subject,page=page )
    return render(request,'TransferGuide/sisForm.html', context = {'form':form})

def generateURL(term,instructor,subject,page):
    url = api_default_url + "&term=" + term
    if (instructor != "None"):
        url += "&instructor_name=" + instructor
    if (subject != "None"):
        url += "&subject=" + subject
    if (page != None):
        url += "&page=" + str(page)
    return url
def apiResult(request, term,instructor, subject,page):
    url = generateURL(term,instructor,subject,page)
    print(url)

    result = requests.get(url)
    resultDict = result.json()
    #print(resultDict)
    display = {'headers' : ['acad_group','acad_org','catalog_nbr','descr','units'],
              'rows': []}
    i=-1
    rows = []
    for c in resultDict:
        rows.append([])
        i+=1
        for item in display.get('headers'):
            rows[i].append(c[item])
    for elem in rows:
        if (elem not in display.get('rows') and elem[4] != "0"):
            display.get('rows').append(elem)
        print(elem)
    display['headers']= ['School','Subject','Course Number', 'Course Title', 'Credits' ]
    return render(request,'TransferGuide/searchResult.html', {'field': display, 'page': page})

def adminApproveCourses(request):
    courses = Course.objects.filter()
    coursesFilter = OrderCourses(request.GET, queryset=courses)
    courses = coursesFilter.qs
    requests = []
    pendingRequests = []
    approvedRequests = []
    deniedRequests = []
    for course in courses:
            a_request = Request.objects.get(foreign_course=course)
            if (a_request.status == "A"):
                approvedRequests.append(a_request)
            elif (a_request.status == "D_LowGrade" or a_request.status == "D_BadFit"):
                deniedRequests.append(a_request)
            else:
                pendingRequests.append(a_request)
    return render(request, 'TransferGuide/adminApproval.html', { 'courses': courses, 'coursesFilter': coursesFilter , 'approvedRequests' :approvedRequests, 'deniedRequests' :deniedRequests,'pendingRequests' :pendingRequests})

def requestPage(request, pk):
    form = statusForm()
    approved_form = None
    denied_form = None
    the_request = Request.objects.get(pk=pk)
    course = the_request.foreign_course
    if request.method == 'POST':
        if ('status-submit' in request.POST):
            form = statusForm(request.POST)
            if (form.is_valid()):
                the_request.status = form.cleaned_data['status']
                the_request.reviewed_by = request.user
                the_request.save()
                if (form.cleaned_data['status'] == "D"):
                    denied_form = denyForm()
                if (form.cleaned_data['status'] == "A"):
                    approved_form = approveForm()
                if (form.cleaned_data['status'] == "P"):
                    the_request.status = "P"
                    url = reverse(adminApproveCourses)
                    messages.success(request, "Status successfully set to pending.")
                    return HttpResponseRedirect(url)
        if ("deny-submit" in request.POST):
            denied_form = denyForm(request.POST)
            if denied_form.is_valid():
                the_request.status = denied_form.cleaned_data['status']
                the_request.reviewer_comment = denied_form.cleaned_data['reviewer_comment']
                the_request.save()
                url = reverse(adminApproveCourses)
                messages.success(request, "Status successfully set to denied.")
                return HttpResponseRedirect(url)
        if ('approve-submit' in request.POST):
            approved_form = approveForm(request.POST)
            if (approved_form.is_valid()):
                the_request.credits_approved = approved_form.cleaned_data['credits_approved']
                the_request.uva_course = approved_form.cleaned_data['equivalent']  # this line has gotta go but I don't know how
                the_request.reviewer_comment = approved_form.cleaned_data['reviewer_comment']  # uncomment when field is actually available
                the_request.reviewed_by = request.user
                the_request.save()
                messages.success(request, 'Request status successfully set to approved.')
                url = reverse(adminApproveCourses)
                return HttpResponseRedirect(url)
    return render(request, 'TransferGuide/requestPage.html', {'course': course, 'form':form, 'approveForm':approved_form, "denyForm" : denied_form})

def searchForCourse(request):
    form = searchCourseForm()
    # select approved courses
    approved_requests = Request.objects.filter(Q(status='A') | Q(status='D_LowGrade'))
    if request.method == 'POST':
        form = searchCourseForm(request.POST)
        if form.is_valid():
            institution = form.cleaned_data['institution']
            word = form.cleaned_data['word']
            dept_num = form.cleaned_data['dept_num']
            # print(len(result))
            result = return_transfer_courses(dept_num, institution, approved_requests, word)
            # print(len(result))
            return render(request, 'TransferGuide/searchCourseResult.html', {'requests':result})
    return render(request, 'TransferGuide/searchCourse.html', {'form':form})


# def return_transfer_courses(dept_num, institution, approved_requests, word):
#     result = []
#     if institution != "No Preference":
#         approved_requests = approved_requests.filter(foreign_course__course_institution__icontains=institution)
#     # print(len(approved_requests))
#     if word != "":
#         approved_requests = approved_requests.filter(foreign_course__course_name__icontains=word)
#     if dept_num != "":
#         raw_data = dept_num.split()
#         if len(raw_data) >= 1:
#             dept = raw_data[0]
#             approved_requests = approved_requests.filter(uva_course__course_dept__iexact=dept)
#             print(len(approved_requests))
#         if len(raw_data) >= 2:
#             num = raw_data[1]
#             approved_requests = approved_requests.filter(uva_course__course_num=num)
#     for request in approved_requests:
#         transfer = request.foreign_course
#         matched = approved_requests.filter(Q(foreign_course__course_institution=transfer.course_institution) &
#                                            Q(foreign_course__course_dept=tranfer.course_dept) &
#                                            Q(foreign_course__course_num=transfer.course_num))
#         result.append(matched.first())
#
#     return approved_requests

def return_transfer_courses(dept_num, institution, approved_requests, word):
    result = approved_requests
    if institution != "No Preference":
        result = result.filter(foreign_course__course_institution__icontains=institution)
    # print(len(result))
    if word != "":
        result = result.filter(foreign_course__course_name__icontains=word)
    if dept_num != "":
        raw_data = dept_num.split()
        if len(raw_data) >= 1:
            dept = raw_data[0]
            result = result.filter(uva_course__course_dept__iexact=dept)
            print(len(result))
        if len(raw_data) >= 2:
            num = raw_data[1]
            result = result.filter(uva_course__course_num=num)
    # create a set of tuples with the unique combination of institution, dept, and num
    unique_tuples = set((r.foreign_course.course_institution, r.foreign_course.course_dept, r.foreign_course.course_num) for r in result)
    # create a list of the first matching request for each unique combination of institution, dept, and num
    result_list = [result.filter(foreign_course__course_institution__iexact=t[0], foreign_course__course_dept__iexact=t[1], foreign_course__course_num=t[2]).first() for t in unique_tuples]
    # filter out None values from the result_list
    result_list = list(filter(None, result_list))
    # create a QuerySet from the result_list
    result_queryset = Request.objects.none()
    for request in result_list:
        result_queryset |= Request.objects.filter(pk=request.pk)
    return result_queryset


def index(request):
    if request.user.is_authenticated:
        username = request.user
        user = UserType.objects.filter(user=username)
        user = user.filter(role='Admin')
        if len(user) == 1: # user is an admin
            own_requests = Request.objects.filter(reviewed_by=username)
            pending_requests = Request.objects.filter(status="P")
        else:
            own_requests = Request.objects.filter(foreign_course__username=username)
            pending_requests = own_requests.filter(status='P')
        accepted_requests = own_requests.filter(status='A')
        denied_requests = own_requests.filter(Q(status='D_BadFit') | Q(status='D_LowGrade'))
        return render(request, 'index.html', {'pending_requests': pending_requests, 'accepted_requests': accepted_requests,
                                              'denied_requests': denied_requests})
    return render(request, 'index.html')


def allUsers(request):
    #if (UserType.objects.get(user=request.user).role != "Admin"):
        #raise PermissionDenied("Only admin users may access this page.")

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
    #if (UserType.objects.get(user=request.user).role != "Admin"):
        #raise PermissionDenied("Only admin users may access this page.")
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
            new_course.course_num = form.cleaned_data['course_number']
            new_course.course_grade = "C"
            new_course.course_delivery = form.cleaned_data['course_delivery']
            new_course.save()
            the_request.foreign_course = new_course
            the_request.save()
            url = reverse(requestPage,args=[the_request.pk])
            return HttpResponseRedirect(url)

    return render(request, "TransferGuide/knownTransferForm.html", {"form":form})

def UVAEquivalents(request,dept,num):
    dept_num = dept + " " + str(num)
    request_qs = return_transfer_courses(dept_num=dept_num,institution="No Preference",word="",approved_requests = Request.objects.filter(Q(status='A') | Q(status='D_LowGrade')))
    return render(request,'TransferGuide/uvaEquivalentCourses.html',context =  {"courseDept": dept, "courseNum": num, "requests": request_qs })