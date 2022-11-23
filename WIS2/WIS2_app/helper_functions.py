from typing import Dict
from django.http.request import HttpRequest
#


def get_user_kind(request: HttpRequest) -> Dict[str: bool]:
  """
  Reads login/session id from cookies and decides what kind of user it is
  Returned dict is in form {user: bool, lecturer: bool, garant: bool}
  """
