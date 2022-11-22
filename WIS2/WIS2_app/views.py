from django.http.request import HttpRequest
from django.shortcuts import render
from WIS2_app.models import Course
from .forms import CreateCourseForm
from .models import Course

def index(request: HttpRequest):
  return render(request, "WIS2_app/index.html", {})


def user(request: HttpRequest):

  return render(request, "WIS2_app/user.html", {})


def courses(request: HttpRequest):
  if request.method == 'POST':
    form = CreateCourseForm(request.POST)
    if form.is_valid():
      form.save()
  else:
    form = CreateCourseForm()

  return render(request, "WIS2_app/courses.html", {'form': form})

def new_course(request: HttpRequest):
  if request.method == 'POST':
    pass
  else:
    pass


def index2(request, name):
  course = Course.objects.get(name=name)
  name = course.name
  return Httprequest("<h1>%s</h1>" % name)
