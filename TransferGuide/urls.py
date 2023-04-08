"""TransferGuide URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'TransferGuide'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="home"),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),
    path('requestCourse/', views.requestCourse, name='requestCourse'),
    path('tryAgain/', views.tryAgain, name="tryAgain"),
    path('requestCourseList', views.requestCourseList, name='requestCourseList'),
    path('sisRequest', views.SISFormHandler, name = 'sisFormHandler'),
    path('sisRequest/<str:term>/<str:instructor>/<str:subject>/', views.apiResult, name='apiResult'),
    path('adminApproval',views.adminApproveCourses, name = 'adminApproveCourses'),
    path('courses/<int:pk>/', views.coursePage, name = 'coursePage'),
    path('submitViableCourse/', views.submitViableCourse, name = 'submitViableCourse'),
    path('seeViableCourse/', views.seeViableCourse, name = 'seeViableCourse')
]
