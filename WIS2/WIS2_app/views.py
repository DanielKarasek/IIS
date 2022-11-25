from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import django.core.exceptions
from django.db.models import Q, Count
from .forms import CreateCourseForm
from .models import *
from django.http.response import HttpResponse
from .helper_functions import get_user_kind

def index(request: HttpRequest) -> HttpResponse:
    user_kind = get_user_kind(request)

    return render(request, "WIS2_app/index.html", user_kind)


def user(request: HttpRequest) -> HttpResponse:

    return render(request, "WIS2_app/user/user.html", {})


def courses(request: HttpRequest) -> HttpResponse:
    user_kind = get_user_kind(request)
    registered_courses = []
    if user_kind["user"]:
        # try to extract user courses
        registered_courses = (Course.objects.
                              select_related().
                              annotate(count=Count('student')).
                              filter(student__UserUID__exact=request.user.id).
                              all())
    not_registered = (Course.objects.
                      select_related().
                      exclude(student__UserUID__exact=request.user.id).
                      annotate(count=Count('student')).
                      all())

    # get all existing courses
    return render(request, "WIS2_app/courses.html", {'course_list': not_registered,
                                                     'registered_course_list': registered_courses,
                                                     **user_kind})


@login_required
def courses_join(request: HttpRequest, course_uid) -> HttpResponse:
    #if the user is already in the course do nothing
    try:
        _course = Course.objects.get(Q(UID=course_uid))
        students = Student.objects.select_related('CourseUID').filter(CourseUID__exact=course_uid).count()
        print(students, _course.student_limit)
        if students >= _course.student_limit:
            return redirect('/courses/')
    except django.core.exceptions.ObjectDoesNotExist:
        return redirect('/courses/')
    try:
        _student = Student.objects.get(UserUID__exact=request.user.id, CourseUID__exact=course_uid)
    except django.core.exceptions.ObjectDoesNotExist:
        new_student = Student()
        new_student.CourseUID = _course
        new_student.UserUID = request.user
        #confirmed status
        new_student.save()

    #vytvorit asi aj body k terminom tuna?
    return redirect('/courses/')


@login_required
def courses_leave(request: HttpRequest, course_uid) -> HttpResponse:
    try:
        _course = Course.objects.get(Q(UID=course_uid))
        _student = (Student.objects.
                    select_related("CourseUID").
                    filter(UserUID__exact=request.user.id).
                    filter(CourseUID__exact=course_uid))
    except django.core.exceptions.ObjectDoesNotExist:
        return redirect('/courses/')

    _student.delete()

    return redirect('/courses/')


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


def courses_detail(request: HttpRequest, course_uid: str) -> HttpResponse:
  course_query_res = Course.objects.filter(UID__exact=course_uid).all()

  if not len(course_query_res):
    return redirect("/courses/")

  period_terms = (TerminPeriod.objects.
                  select_related('TerminID').
                  filter(TerminID__CourseUID__exact=course_uid))

  single_terms = (TerminSingle.objects.
                  select_related('TerminID').
                  filter(TerminID__CourseUID__exact=course_uid))

  course = course_query_res[0]

  exam_list = single_terms.filter(kind__exact="EXM").all()
  project_list = single_terms.filter(kind__exact="PRJ").all()
  lecture_list = period_terms.filter(kind__exact="LEC").all()
  practice_lecture_list = period_terms.filter(kind__exact="PLEC").all()
  print(get_user_kind(request))
  return render(request, "WIS2_app/course_details.html",
                {'user': True,
                 'course': course,
                 'exam_list': exam_list,
                 'project_list': project_list,
                 'lecture_list': lecture_list,
                 'practice_lecture_list': practice_lecture_list})
