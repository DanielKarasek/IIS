from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import CreateRoomForm
import django.core.exceptions
from .models import Course


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
    try:
        rooms = Room.objects.get(roomUID=room_uid)
        rooms.delete()
    except django.core.exceptions.ObjectDoesNotExist:
        pass
    return redirect('/admin/rooms/')
