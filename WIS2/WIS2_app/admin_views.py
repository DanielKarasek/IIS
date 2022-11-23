from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from .models import *
from .forms import CreateRoomForm
import django.core.exceptions
from .models import Course


def room(request: HttpRequest):
    if request.method == 'POST':
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = CreateRoomForm()
    try:
        rooms = Room.objects.all()
        print(rooms)
    except django.core.exceptions.ObjectDoesNotExist:
        rooms = []
    return render(request, "WIS2_app/admin/rooms.html", {"form": form,
                                                         "rooms": rooms})


def room_delete(request: HttpRequest, room_uid):
    try:
        rooms = Room.objects.get(roomUID=room_uid)
        rooms.delete()
    except django.core.exceptions.ObjectDoesNotExist:
        pass
    return redirect('/admin/rooms/')
