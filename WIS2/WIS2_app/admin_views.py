
from django.contrib.auth.decorators import login_required
import django.core.exceptions
from django.db.models import Q
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render, redirect

import http.client

from .forms import CreateRoomForm
from .helper_functions import get_user_kind
from .models import *
from .models import Garant


@login_required
def manage_room_view(request: HttpRequest) -> HttpResponse:
    """
    Create/delete view for admin
    """
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
                                                         "rooms": rooms,
                                                         **get_user_kind(request)})


@login_required
def garant_managment_view(request: HttpRequest) -> HttpResponse:
    """
    View for garant managment (allowing/disallowing courses)
    """
    try:
        garants_confirmed = Garant.objects.filter(confirmed=True).all()
    except django.core.exceptions.ObjectDoesNotExist:
        garants_confirmed = []
    try:
        garants_unconfirmed = Garant.objects.filter(confirmed=False).all()
    except django.core.exceptions.ObjectDoesNotExist:
        garants_unconfirmed = []

    return render(request, "WIS2_app/admin/garants.html", {"garants_waiting": garants_unconfirmed,
                                                          "garants_verified": garants_confirmed,
                                                          **get_user_kind(request)})


@login_required
def garants_change_confirmed(request: HttpRequest, course_uid: str) -> http.client.responses:
    """
    Action when allow/disallow is clicked for any course in garant_managment_view.py
    """
    if request.user.is_staff:
        try:
            _garant = Garant.objects.get(Q(CourseUID=course_uid))
            _garant.confirmed = not (_garant.confirmed)
            _garant.save()
        except django.core.exceptions.ObjectDoesNotExist:
            pass
    return redirect('/admin/garants/')



@login_required
def room_delete(request: HttpRequest, room_uid: str) -> HttpResponse:
    """
    Action on delete room button pressed
    """
    if request.user.is_staff:
        try:
            rooms = Room.objects.get(roomUID=room_uid)
            rooms.delete()
        except django.core.exceptions.ObjectDoesNotExist:
            pass
    return redirect('/admin/rooms/')
