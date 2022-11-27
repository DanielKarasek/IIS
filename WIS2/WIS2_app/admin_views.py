from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from .forms import CreateRoomForm
import django.core.exceptions
from .models import Course, Garant


@login_required
def room(request: HttpRequest):
    if request.method == 'POST':
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = CreateRoomForm()
    try:
        rooms = Room.objects.all()
    except django.core.exceptions.ObjectDoesNotExist:
        rooms = []
    return render(request, "WIS2_app/admin/rooms.html", {"form": form,
                                                         "rooms": rooms})


@login_required
def room_delete(request: HttpRequest, room_uid):
    if request.user.is_staff:
        try:
            rooms = Room.objects.get(roomUID=room_uid)
            rooms.delete()
        except django.core.exceptions.ObjectDoesNotExist:
            pass
    return redirect('/admin/rooms/')


@login_required
def garants(requst: HttpRequest):
    try:
        garants_confirmed = Garant.objects.get(Q(confirmed=True))
        garants_unconfirmed = Garant.objects.get(Q(confirmed=False))
    except django.core.exceptions.ObjectDoesNotExist:
        garants_confirmed = []
        garants_unconfirmed = []

    pass


@login_required
def garants_change_confirmed(request: HttpRequest, course_uid):
    if request.user.is_staff:
        try:
            _garant = Garant.objects.get(Q(CourseUID=course_uid))
            _garant.confirmed = not (_garant.confirmed)
            _garant.save()
        except django.core.exceptions.ObjectDoesNotExist:
            pass
    return redirect('/admin/garants/')
