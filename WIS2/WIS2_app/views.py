from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import django.core.exceptions
from django.db.models import Q, Count
from .forms import (CreateCourseForm, CreateTerminForm, CreateProjectForm,
                    CreateLectureForm, CreateExamForm, CreatePracticeLectureForm)
from .models import *
from django.http.response import HttpResponse
from .helper_functions import get_user_kind


def index(request: HttpRequest) -> HttpResponse:
    user_kind = get_user_kind(request)

    return render(request, "WIS2_app/index.html", user_kind)


def user(request: HttpRequest) -> HttpResponse:
  user_kind = get_user_kind(request)

  return render(request, "WIS2_app/user/user.html", user_kind)


@login_required
def create_termin(request: HttpRequest, termin_type: str, course_uid: str):
  user_kind = get_user_kind(request)
  termin_type2form = {'lecture': CreateLectureForm,
                      'practice_lecture': CreatePracticeLectureForm,
                      'exam': CreateExamForm,
                      'project': CreateProjectForm}
  termin_type2cz = {'lecture': 'přednášky',
                    'practice_lecture': 'cvičení',
                    'exam': 'zkoušky',
                    'project': 'projektu'}
  if request.method == 'POST':
    form = termin_type2form[termin_type](request.POST)
    if form.is_valid():
      form.save(course_uid)
      return redirect('/courses/detail/' + course_uid)
  else:
    form = termin_type2form[termin_type]()
  try:
    course = Course.objects.get(UID__exact=course_uid)
  except django.core.exceptions.ObjectDoesNotExist:
    return redirect('/courses/')

  return render(request, "WIS2_app/user/create_termin.html", {'form': form,
                                                              'course_name': course.name,
                                                              'termin_type': termin_type2cz[termin_type],
                                                              **user_kind})

def courses(request: HttpRequest) -> HttpResponse:
    user_kind = get_user_kind(request)
    registered_courses = []
    not_registered = (Course.objects.
                      select_related().
                      annotate(count=Count('student')))
    if user_kind["user"]:
        # try to extract user courses
        registered_courses = (Course.objects.
                              select_related().
                              annotate(count=Count('student')).
                              filter(student__UserUID__exact=request.user.id).
                              all())

        not_registered = (not_registered.
                          exclude(student__UserUID__exact=request.user.id))

    not_registered = not_registered.all()

    # get all existing courses
    return render(request, "WIS2_app/courses.html", {'course_list': not_registered,
                                                     'registered_course_list': registered_courses,
                                                     **user_kind})

@login_required
def my_courses(request: HttpRequest) -> HttpResponse:
    user_kind = get_user_kind(request)
    registered_courses = []
    if user_kind["user"]:
        # try to extract user courses
        registered_courses = (Student.objects.
                              select_related('CourseUID').
                              filter(UserUID__exact=request.user.id).
                              all())

    # get all existing courses
    return render(request, "WIS2_app/user/my_courses.html", {'registered_course_list': registered_courses, **user_kind})

@login_required
def courses_join(request: HttpRequest, course_uid) -> HttpResponse:
    # Check if course exists and if student limit allows new students
    try:
        _course = Course.objects.get(Q(UID=course_uid))
        students = Student.objects.select_related('CourseUID').filter(CourseUID__exact=course_uid).count()
        if students >= _course.student_limit:
            return redirect('/courses/')
    except django.core.exceptions.ObjectDoesNotExist:
        return redirect('/courses/')

    # if the user is already in the course do nothing
    _student = Student.objects.filter(UserUID__exact=request.user.id, CourseUID__exact=course_uid).first()
    _garant = Garant.objects.filter(Q(UserUID=request.user) & Q(CourseUID=_course)).first()
    _teacher = Teacher.objects.filter(Q(UserUID=request.user) & Q(CourseUID=_course)).first()
    if _student or _teacher or _garant:
      return redirect('/courses/')

    new_student = Student()
    new_student.CourseUID = _course
    new_student.UserUID = request.user
    # confirmed status
    new_student.save()

    # vytvorit asi aj body k terminom tuna?
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
            _garant = Garant()
            _garant.CourseUID = Course.objects.get(Q(UID=form.cleaned_data['uid']))
            _garant.UserUID = request.user
            _garant.save()
    else:
        form = CreateCourseForm()

    return render(request, "WIS2_app/user/create_course.html", {'form': form})


@login_required
def course_termin_create(request: HttpRequest, course_uid) -> HttpResponse:
    if request.method == 'POST':
        form = CreateTerminForm(request.POST)
        if form.is_valid():
            #ci ideme periodicky termin alebo single
            if request.POST.get("periodic"):
                form.save("periodic", course_uid)
                return redirect('/courses/detail/' + course_uid)
            if request.POST.get("single"):
                form.save("single", course_uid)
                return redirect('/courses/detail/' + course_uid)
    else:
        form = CreateTerminForm()

    return render(request, "WIS2_app/user/create_termin.html", {'form': form})


@login_required
def new_course(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        pass
    else:
        pass


def courses_detail(request: HttpRequest, course_uid: str) -> HttpResponse:
    course_query_res = Course.objects.filter(UID__exact=course_uid).all()

    if not len(course_query_res):
        return redirect("/courses/")
    if request.POST.get("add"):
        return redirect("/courses/create_termin/" + course_uid)

    period_terms = (TerminPeriod.objects.
                    select_related('TerminID').
                    filter(TerminID__CourseUID__exact=course_uid))

    single_terms = (TerminSingle.objects.
                    select_related('TerminID').
                    filter(TerminID__CourseUID__exact=course_uid))

    course = course_query_res[0]
    print(course)

    exam_list = single_terms.filter(kind__exact="EXM").all()
    project_list = single_terms.filter(kind__exact="PRJ").all()
    lecture_list = period_terms.filter(kind__exact="LEC").all()
    practice_lecture_list = period_terms.filter(kind__exact="PLEC").all()
    return render(request, "WIS2_app/course_details.html",
                  {'user': True,
                   'course': course,
                   'exam_list': exam_list,
                   'project_list': project_list,
                   'lecture_list': lecture_list,
                   'practice_lecture_list': practice_lecture_list})


@login_required
def termins(request: HttpRequest) -> HttpResponse:
    # get registered courses
    user_kind = get_user_kind(request)
    registered_courses = []
    if user_kind["user"]:
        # try to extract user courses
        registered_courses = (Student.objects.
                              select_related('CourseUID').
                              filter(UserUID__exact=request.user.id).
                              all())
    return render(request, "WIS2_app/courses/course_termins.html", {'user': True,
                                                                    'course_list': registered_courses})


@login_required
def termins_course(request: HttpRequest, course_uid):
    user_kind = get_user_kind(request)
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

    return render(request, "WIS2_app/courses/course_termins_detail.html")
