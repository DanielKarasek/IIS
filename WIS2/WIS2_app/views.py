from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import django.core.exceptions
from django.db.models import Q, Count
from .forms import (CreateCourseForm, CreateProjectForm,
                    CreateLectureForm, CreateExamForm, CreatePracticeLectureForm)
from .models import *
from django.http.response import HttpResponse
from .helper_functions import get_user_kind
import django.contrib.messages as messages


def index(request: HttpRequest) -> HttpResponse:
    user_kind = get_user_kind(request)

    return render(request, "WIS2_app/index.html", {**user_kind})


def user(request: HttpRequest) -> HttpResponse:
  user_kind = get_user_kind(request)

  return render(request, "WIS2_app/user/user.html", {**user_kind})


@login_required
def user_change_password(request: HttpRequest) -> HttpResponse:
  if request.method == 'POST':
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
      user = form.save()
      update_session_auth_hash(request, user)  # Important!
      messages.success(request, 'Vaše heslo bylo úspěšně změněno')
    else:
      messages.error(request, 'Prosím opravte následující chyby: ')
  else:
    form = PasswordChangeForm(request.user)
  return render(request, 'WIS2_app/user/change_password.html', {
    'form': form
  })


@login_required
def user_delete(request: HttpRequest) -> HttpResponse:
  request.user.delete()
  return redirect('/logout/')


# KURZY stuff general
def courses(request: HttpRequest) -> HttpResponse:
    user_kind = get_user_kind(request)
    registered_courses = []
    garanting = []
    teaching = []
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

        garanting = not_registered.filter(garant__UserUID__exact=request.user.id).all()
        teaching = not_registered.filter(teacher__UserUID__exact=request.user.id).all()

        not_registered = (not_registered.
                          exclude(student__UserUID__exact=request.user.id).
                          exclude(garant__UserUID__exact=request.user.id).
                          exclude(teacher__UserUID__exact=request.user.id).
                          exclude(garant__confirmed__isnull=True).
                          exclude(garant__confirmed=False))

    not_registered = not_registered.all()

    # get all existing courses
    return render(request, "WIS2_app/courses.html", {'not_registered': not_registered,
                                                     'registered_course_list': registered_courses,
                                                     'garanting': garanting,
                                                     'teaching': teaching,
                                                     **user_kind})


@login_required
def courses_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            course_tmp1 = Course.objects.filter(UID__exact=form.cleaned_data['uid']).first()
            course_tmp2 = Course.objects.filter(name__exact=form.cleaned_data['name']).first()
            if course_tmp1 or course_tmp2:
              messages.error(request, "Kurz s tímto názvem nebo zkratkou již existuje")
              return render(request, "WIS2_app/user/create_course.html", {'form': form})
            else:
              form.save()
              _garant = Garant()
              _garant.CourseUID = Course.objects.get(Q(UID=form.cleaned_data['uid']))
              _garant.UserUID = request.user
              _garant.save()

        return redirect("/courses/")
    else:
        form = CreateCourseForm()

    return render(request, "WIS2_app/user/create_course.html", {'form': form})

@login_required
def courses_delete(request, course_uid):
    is_garant = (Garant.objects.
                 filter(CourseUID__exact=course_uid, UserUID__exact=request.user.id).
                 filter(confirmed=True).
                 first())
    if request.user.is_staff or (is_garant):
        _course = Course.objects.get(Q(UID=course_uid))
        _course.delete()
    return redirect('/courses/')


def courses_detail(request: HttpRequest, course_uid: str) -> HttpResponse:
    course_query_res = Course.objects.filter(UID__exact=course_uid).all()

    if not len(course_query_res):
        return redirect("/courses/")
    if request.POST.get("add"):
        return redirect("/courses/create_termin/" + course_uid)

    is_garant = (Garant.objects.
                 filter(CourseUID__exact=course_uid, UserUID__exact=request.user.id).
                 filter(confirmed=True).
                 first())

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
    return render(request, "WIS2_app/course_details.html",
                  {'course': course,
                   'exam_list': exam_list,
                   'project_list': project_list,
                   'lecture_list': lecture_list,
                   'practice_lecture_list': practice_lecture_list,
                   'is_course_garant': is_garant,
                   **get_user_kind(request)})


# Kurzy interakce s uzivatelem
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

###
# Termin stuff
###
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


def delete_termin(request: HttpRequest, course_uid: str, termin_uid: str) -> HttpResponse:
  try:
    _ = Course.objects.get(UID__exact=course_uid)
    termin = Termin.objects.get(ID__exact=termin_uid)
  except django.core.exceptions.ObjectDoesNotExist:
    return redirect(f'/courses/detail/{course_uid}/')

  termin.delete()
  return redirect(f'/courses/detail/{course_uid}')


###
### TOTO JE NA HODNOTENIE postupne presmerovava ako klikas buttons najrpv z kurzov potom na terminy a studentov
###
def evaluation(request: HttpRequest) -> HttpResponse:
    #get courses where garant or teacher
    _garant = Garant.objects.filter(UserUID=request.user).filter(confirmed=True).all()
    _teacher = Teacher.objects.filter(UserUID=request.user).all()
    All_courses = []
    if len(_garant):
        for item in _garant:
            All_courses.append(Course.objects.get(Q(UID=item.CourseUID.UID)))
    if len(_teacher):
        for item in _teacher:
            All_courses.append(Course.objects.get(Q(UID=item.CourseUID.UID)))
    return render(request, "WIS2_app/user/student_evaluation.html", {'course_list': All_courses})

def evaluation_termin(request: HttpRequest, course_uid) -> HttpResponse:

    period_terms = (TerminPeriod.objects.
                    select_related('TerminID').
                    filter(TerminID__CourseUID__exact=course_uid))

    single_terms = (TerminSingle.objects.
                    select_related('TerminID').
                    filter(TerminID__CourseUID__exact=course_uid))


    exam_list = single_terms.filter(kind__exact="EXM").all()
    project_list = single_terms.filter(kind__exact="PRJ").all()
    lecture_list = period_terms.filter(kind__exact="LEC").all()
    practice_lecture_list = period_terms.filter(kind__exact="PLEC").all()
    return render(request, "WIS2_app/user/evaluation_termin.html",
                  {'course': course_uid,
                   'exam_list': exam_list,
                   'project_list': project_list,
                   'lecture_list': lecture_list,
                   'practice_lecture_list': practice_lecture_list})


def evaluation_student(request: HttpRequest, course_uid, termin_uid) -> HttpResponse:
    student_list = Course.objects.get(UID__exact = course_uid).student_set.all()
    termin2body_list = Termin.objects.get(ID__exact = termin_uid).termin2body_set.all()
    return render(request, "WIS2_app/user/evaluation_student.html", {'student_list': student_list,
                                                                     'termin_uid': termin2body_list})

def evaluation_student_body(request: HttpRequest, course_uid, termin_uid, user_uid) -> HttpResponse:
    #print(TerminSingle.objects.get(TerminID__exact=termin_uid))
    #print(Termin.objects.get(ID__exact= termin_uid).kind)
    #print(User.objects.get(username__exact = user_uid).id)
    if request.method == 'POST':
        form = CreateTermin2Body(request.POST)
        if form.is_valid():
            form.save(request, course_uid, termin_uid, user_uid)
    else:
        form = CreateTermin2Body()

    return render(request, 'WIS2_app/user/add_body_student.html', {'form': form})

