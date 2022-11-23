from django.http.request import HttpRequest
from django.shortcuts import render
from .forms import CreateCourseForm
from .models import Course
from django.http.response import HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "WIS2_app/index.html", {'user': False, 'garant': False, 'lecturer': False})


def user(request: HttpRequest) -> HttpResponse:
    return render(request, "WIS2_app/user/user.html", {})


def courses(request: HttpRequest) -> HttpResponse:
  return render(request, "WIS2_app/courses.html", {'course_list': Course.objects.all(), 'user': True})


def create_course(request: HttpRequest) -> HttpResponse:
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
