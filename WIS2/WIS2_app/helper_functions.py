from typing import Dict
from django.http.request import HttpRequest
from .models import *
#


def get_user_kind(request: HttpRequest) -> Dict[str, bool]:
  """
  Reads login/session id from cookies and decides what kind of user it is
  Returned dict is in form {user: bool, lecturer: bool, garant: bool}
  """

  user_kind_dict = {"user": False, "garant": False, "lecturer": False}
  if not request.user.is_authenticated:
    return user_kind_dict
  user_kind_dict["user"] = True
  if len(Garant.objects.filter(UserUID__exact=request.user).all()):
    user_kind_dict["garant"] = True
  if len(Teacher.objects.filter(UserUID__exact=request.user).all()):
    user_kind_dict["lecturer"] = True

  return user_kind_dict
