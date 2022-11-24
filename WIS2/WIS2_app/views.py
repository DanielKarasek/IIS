from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import django.core.exceptions
from .forms import CreateCourseForm
from .models import Course
from django.http.response import HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "WIS2_app/index.html", {'user': False, 'garant': False, 'lecturer': False})


def user(request: HttpRequest) -> HttpResponse:

    return render(request, "WIS2_app/user/user.html", {})


def courses(request: HttpRequest) -> HttpResponse:
    user_logged_in = False
    if request.user.is_authenticated:
        user_logged_in = True

    _courses = []
    try:
        _courses = Course.objects.all()
    except django.core.exceptions.ObjectDoesNotExist:
        pass
    return render(request, "WIS2_app/courses.html", {'course_list': _courses, 'user': user_logged_in})


@login_required
def courses_join(request: HttpRequest, course_uid) -> HttpResponse:

    return redirect('courses/')


@login_required
def courses_leave(request: HttpRequest, course_uid) -> HttpResponse:

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
