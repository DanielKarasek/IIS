from typing import Dict
from django.http.request import HttpRequest
from django.db.models import Q, Count
import django.core.exceptions
from .models import *


#


def get_user_kind(request: HttpRequest) -> Dict[str, bool]:
    """
    Reads login/session id from cookies and decides what kind of user it is
    Returned dict is in form {user: bool, lecturer: bool, garant: bool}
    """

    user_kind_dict = {"user": False, "garant": False, "lecturer": False, "admin": False}
    if not request.user.is_authenticated:
        return user_kind_dict
    if request.user.is_staff:
        user_kind_dict["admin"] = True

    user_kind_dict["user"] = True
    if len(Garant.objects.filter(UserUID__exact=request.user).all()):
        user_kind_dict["garant"] = True
    if len(Teacher.objects.filter(UserUID__exact=request.user).all()):
        user_kind_dict["lecturer"] = True

    return user_kind_dict


def get_body_termin(TerminUID, StudentUID):
    try:
        _termin = Termin2Body.objects.get(Q(TerminUID=TerminUID) & Q(StudentUID=StudentUID))
    except django.core.exceptions.ObjectDoesNotExist:
        return 0
    return _termin.points_given


def get_body_course(CourseUID, StudentUID):
    body = 0

    _termins = Termin.objects.filter(CourseUID=CourseUID).all()
    if not len(_termins):
        return body

    for _termin in _termins:
        body = body + get_body_termin(_termin.ID, StudentUID)

    return body
