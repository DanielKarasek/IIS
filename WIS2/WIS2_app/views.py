from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import django.core.exceptions
from django.db.models import Q
from .forms import CreateCourseForm
from .models import *
from django.http.response import HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "WIS2_app/index.html", {'user': False, 'garant': False, 'lecturer': False})


def user(request: HttpRequest) -> HttpResponse:

    return render(request, "WIS2_app/user/user.html", {})


def courses(request: HttpRequest) -> HttpResponse:
    user_logged_in = False
    registered_courses = []
    if request.user.is_authenticated:
        #show registered course list and buttons
        user_logged_in = True

        #try to extract user courses
        try:
            registered_courses = Student.CourseUID.objects.all()
        except django.core.exceptions.ObjectDoesNotExist:
            pass

    #get all existing courses
    _courses = []
    try:
        _courses = Course.objects.all()
    except django.core.exceptions.ObjectDoesNotExist:
        pass
    return render(request, "WIS2_app/courses.html", {'course_list': _courses,
                                                     'registered_course_list': registered_courses,
                                                     'user': user_logged_in})


@login_required
def courses_join(request: HttpRequest, course_uid) -> HttpResponse:
    #if the user is already in the course do nothing
    try:
        _course = Course.objects.get(Q(UID=course_uid))
        _student = Student.objects.get(Q(UserUID=request.user) and Q(CourseUID=_course))
    except django.core.exceptions.ObjectDoesNotExist:
        return redirect('courses/')

    if _student:
        return redirect('courses/')
    else:
        new_student = Student()
        new_student.CourseUID = _course
        new_student.UserUID = request.user
        #confirmed status
        new_student.save()

    #vytvorit asi aj body k terminom tuna?

    return redirect('courses/')


@login_required
def courses_leave(request: HttpRequest, course_uid) -> HttpResponse:
    try:
        _course = Course.objects.get(Q(UID=course_uid))
        _student = Student.objects.get(Q(UserUID=request.user) and Q(CourseUID=_course))
    except django.core.exceptions.ObjectDoesNotExist:
        return redirect('courses/')

    if _student:
        _student.delete()

    return redirect('courses/')


@login_required
def courses_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = CreateCourseForm()

    return render(request, "WIS2_app/user/create_course.html", {'form': form})


def new_course(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        pass
    else:
        pass


def course_detail(request: HttpRequest, course_uid: str) -> HttpResponse:
  course_query_res = Course.objects.filter(UID__exact=course_uid).all()

  if not len(course_query_res):
    return redirect("courses/")

  period_terms = (Termin.objects.
                  filter(CourseUID__exact=course_uid).
                  select_related("CourseUID").
                  select_related("terminperiod"))
  single_terms = (Termin.objects.
                  filter(CourseUID__exact=course_uid).
                  select_related("CourseUID").
                  select_related("terminsingle").
                  filter(kind__exact='LEC'))

  course = course_query_res[0]

  exam_list = single_terms.filter(kind__exact="EXM").all()
  project_list = single_terms.filter(kind__exact="PRJ").all()
  lecture_list = period_terms.filter(kind__exact="LEC").all()
  practice_lecture_list = period_terms.filter(kind__exact="PLEC").all()
  print(exam_list)
  return render(request, "WIS2_app/course_details.html",
                {'user': True,
                 'course': course,
                 'exam_list': exam_list,
                 'project_list': project_list,
                 'lecture_list': lecture_list,
                 'practice_lecture_list': practice_lecture_list})
