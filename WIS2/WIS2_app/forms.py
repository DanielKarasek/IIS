from datetime import datetime

from django import forms
from django.http.request import HttpRequest

from .models import *
from .validators import validate_is_positive


# These are used because the code is in different language than target audience language
LANGUAGES = [('ENG', 'Angličtina'),
             ('CZE', 'Čeština'),
             ('GER', 'Němčina')]

COURSE_KINDS = [
    ('REQ', 'Povinný'),
    ('CHO', 'Povinně volitelný'),
    ('FRE', 'Volitelný'),
]

TERMIN_KINDS = [
    ('PER', 'Periodický'),
    ('ONE', 'Jednorázový'),
]
TERMIN_TYPE =[
    ('PLEC', 'Cvičení'),
    ('LEC', 'Přednáška'),
    ('EXM', "Zkouška"),
    ('PRJ', "Projekt"),
]


class CreateCourseForm(forms.Form):
    """
    This class generates forms for course creation
    """
    uid = forms.CharField(label="* Zkratka:", max_length=5, required=True)
    name = forms.CharField(label="* Celý název:", max_length=40, required=True)

    kind = forms.CharField(label="* Druh kurzu:", required=True,
                           widget=forms.Select(choices=COURSE_KINDS))

    credit = forms.IntegerField(label="* Kredity", required=True,
                                validators=[validate_is_positive], min_value=1, max_value=30)

    students = forms.IntegerField(label="* Limit Studentů:", required=True,
                                  validators=[validate_is_positive], min_value=1, max_value=999)

    lang = forms.CharField(label="* Jazyk:", max_length=3, required=True, widget=forms.Select(choices=LANGUAGES))

    desc = forms.CharField(label="* Popis:", required=True,
                           widget=forms.Textarea)

    def save(self, user: User):
        course = Course()
        course.UID = self.cleaned_data['uid']
        course.name = self.cleaned_data['name']
        course.kind = self.cleaned_data['kind']
        course.credits = self.cleaned_data['credit']
        course.student_limit = self.cleaned_data['students']
        course.language = self.cleaned_data['lang']
        course.description = self.cleaned_data['desc']

        course.save()

        garant = Garant()
        garant.CourseUID = Course.objects.get(UID__exact=self.cleaned_data['uid'])
        garant.UserUID = user
        garant.save()
        teacher = Teacher()
        teacher.CourseUID = Course.objects.get(UID__exact=self.cleaned_data['uid'])
        teacher.UserUID = user
        teacher.save()


class CreateRoomForm(forms.Form):
    """
    This class generates forms for room creation
    """
    uid = forms.CharField(label="* Jméno místnosti:", max_length=10, required=True)

    def save(self):
        room = Room()
        room.roomUID = self.cleaned_data['uid']
        room.save()


class GeneralTermForm(forms.Form):
  """
  This class generates forms for general term creation
  """
  name = forms.CharField(label="* Jméno:", required=True)
  room = forms.ModelChoiceField(label="* Místnost:", queryset=Room.objects.all(), required=True)
  points = forms.IntegerField(label="* Maximum bodů:", required=True, min_value=0)
  desc = forms.CharField(label="Popis", required=False,
                         widget=forms.Textarea)
  kind_perxsingle = None

  def save(self, course_uid: str) -> Termin:
    termin = Termin()
    termin.CourseUID = Course.objects.get(UID__exact=course_uid)
    termin.name = self.cleaned_data['name']
    termin.RoomUID = Room.objects.get(roomUID__exact=self.cleaned_data['room'].roomUID)
    termin.max_points = self.cleaned_data['points']
    termin.kind = self.kind_perxsingle
    termin.description = self.cleaned_data['desc']
    termin.save()

    return termin


class CreatePeriodicForm(GeneralTermForm):
  """
  This class generates forms for general periodic term creation
  """
  repeats = forms.IntegerField(label="* Celkem opakování:", required=False, min_value=0)
  periodicity = forms.IntegerField(label="* Perioda opakování v týdnech:", required=False, min_value=0)
  date = forms.DateField(label="First date", widget=forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
                         required=True)

  time = forms.TimeField(label="First time", widget=forms.TimeInput(attrs={'type': 'time'}, format="%H:%M"),
                         required=True)
  kind_perxsingle = 'PER'
  kind_plecxlec = None

  def save(self, course_uid: str) -> None:
    termin = super().save(course_uid)

    terminperiodic = TerminPeriodic()
    terminperiodic.kind = self.kind_plecxlec
    terminperiodic.TerminID = Termin.objects.get(ID__exact=termin.ID)
    terminperiodic.start = datetime.combine(self.cleaned_data['date'], self.cleaned_data['time'])
    terminperiodic.repeats = self.cleaned_data['repeats']
    terminperiodic.periodicity = self.cleaned_data['periodicity']
    terminperiodic.save()


class CreateLectureForm(CreatePeriodicForm):
  """
  This class generates forms for lecture creation
  """

  kind_plecxlec = 'LEC'


class CreatePracticeLectureForm(CreatePeriodicForm):
  """
  This class generates forms for practice lecture creation
  """
  kind_plecxlec = 'PLEC'


class CreateOneShotTerm(GeneralTermForm):
  """
  This class generates forms for general one shot term
  """
  date = forms.DateField(label="First date", widget=forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
                         required=True)

  time = forms.TimeField(label="First time", widget=forms.TimeInput(attrs={'type': 'time'}, format="%H:%M"),
                         required=True)
  kind_perxsingle = 'ONE'
  kind_exmxproj = None

  def save(self, course_uid: str) -> None:
    termin = super().save(course_uid)
    terminsingle = TerminSingle()
    terminsingle.TerminID = Termin.objects.get(ID__exact=termin.ID)
    terminsingle.kind = self.kind_exmxproj
    terminsingle.date = datetime.combine(self.cleaned_data['date'],self.cleaned_data['time'])
    terminsingle.save()


class CreateProjectForm(CreateOneShotTerm):
    """
    This class generates forms for projects
    """
    kind_exmxproj = "PRJ"


class CreateExamForm(CreateOneShotTerm):
    """
    This class generates forms exams
    """
    kind_exmxproj = "EXM"


class CreateTermin2Body(forms.Form):
  """
  This class generates forms termin2points table
  """
  body = forms.IntegerField(label="DUMMY overriden in init")
  body_extra = forms.IntegerField(label="Body extra:", required=False)

  def __init__(self, max_body: int = 30, *args, **kwargs):
    super().__init__(*args, *kwargs)
    print(self.__dict__)
    self.fields['body'] = forms.IntegerField(label="* Body:", min_value=0, max_value=max_body, required=True)

  def save(self, request: HttpRequest, course_uid: str, termin_uid: str, user_uid: str) -> None:
    terminbody = Termin2Body()
    already_exists = Termin2Body.objects.filter(TerminUID__exact=Termin.objects.get(ID__exact=termin_uid),
                                                StudentUID__exact=Student.objects.get(
                                                  UserUID__exact=User.objects.get(username__exact=user_uid).id,
                                                  CourseUID__exact=course_uid)).first()
    if already_exists:
      already_exists.delete()

    terminbody.TerminUID = Termin.objects.get(ID__exact=termin_uid)

    terminbody.StudentUID = Student.objects.get(UserUID__exact=User.objects.get(username__exact=user_uid).id,
                                                CourseUID__exact=course_uid)
    terminbody.TeacherUID = Teacher.objects.get(UserUID__exact=User.objects.get(username__exact=request.user).id,
                                                CourseUID__exact=course_uid)

    terminbody.points_given = self.cleaned_data['body'] + self.cleaned_data['body_extra']
    terminbody.save()


class AddLectorForm(forms.Form):
  def __init__(self, request, course_uid, *args, **kwargs):
    super().__init__(*args, **kwargs)
    valid_candidate = (User.objects.select_related().exclude(username__exact=request.user).
                       exclude(student__CourseUID__exact=course_uid).
                       exclude(teacher__CourseUID__exact=course_uid)).all()
    self.fields['userUID'] = forms.ModelChoiceField(label="Lektor:", queryset=valid_candidate,
                                                    required=True)

  def save(self, course_uid):
    teacher = Teacher()
    teacher.UserUID = self.cleaned_data['userUID']
    teacher.CourseUID = Course.objects.get(UID__exact=course_uid)
    teacher.save()
