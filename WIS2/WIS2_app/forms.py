from django import forms
from .models import *
from .validators import validate_is_positive

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

    def save(self, user):
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
    uid = forms.CharField(label="* Jméno místnosti:", max_length=10, required=True)

    def save(self):
        print("got here")
        room = Room()
        room.roomUID = self.cleaned_data['uid']
        room.save()


class GeneralTermForm(forms.Form):
  name = forms.CharField(label="* Jméno:", required=True)
  room = forms.ModelChoiceField(label="* Místnost:", queryset=Room.objects.all(), required=True)
  points = forms.IntegerField(label="* Maximum bodů:", required=True, min_value=0)
  desc = forms.CharField(label="Popis", required=False,
                         widget=forms.Textarea)
  kind_perxsingle = None

  def save(self, course_uid):
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
  repeats = forms.IntegerField(label="* Celkem opakování:", required=False, min_value=0)
  periodicity = forms.IntegerField(label="* Perioda opakování v týdnech:", required=False, min_value=0)
  date = forms.DateTimeField(label="* První termín:", widget=forms.DateTimeInput, input_formats="%Y-%M-%D %H:%M",
                             required=True)

  kind_perxsingle = 'PER'
  kind_plecxlec = None

  def save(self, course_uid):
    termin = super().save(course_uid)
    terminperiodic = TerminPeriod()
    terminperiodic.kind = self.kind_plecxlec
    terminperiodic.TerminID = Termin.objects.get(ID__exact=termin.ID)
    terminperiodic.start = self.cleaned_data['date']
    terminperiodic.repeats = self.cleaned_data['repeats']
    terminperiodic.periodicity = self.cleaned_data['periodicity']
    terminperiodic.save()


class CreateLectureForm(CreatePeriodicForm):
  kind_plecxlec = 'LEC'


class CreatePracticeLectureForm(CreatePeriodicForm):
  kind_plecxlec = 'PLEC'


class CreateOneShotTerm(GeneralTermForm):
  date = forms.DateTimeField(label="* datum", widget=forms.DateTimeInput, input_formats="%Y-%M-%D %H:%M", required=True)
  kind_perxsingle = 'ONE'
  kind_exmxproj = None

  def save(self, course_uid):
    termin = super().save(course_uid)
    terminsingle = TerminSingle()
    terminsingle.TerminID = Termin.objects.get(ID__exact=termin.ID)
    terminsingle.kind = self.kind_exmxproj
    terminsingle.date = self.cleaned_data['date']
    terminsingle.save()


class CreateProjectForm(CreateOneShotTerm):
    kind_exmxproj = "PRJ"


class CreateExamForm(CreateOneShotTerm):
    kind_exmxproj = "EXM"


class CreateTermin2Body(forms.Form):
  body = forms.IntegerField(label="Toto jen dummy at mame spravne poradi po init")
  body_extra = forms.IntegerField(label="Body extra:", required=False)

  def __init__(self, max_body=30, *args, **kwargs):
    super().__init__(*args, *kwargs)
    print(self.__dict__)
    self.fields['body'] = forms.IntegerField(label="* Body:", min_value=0, max_value=max_body, required=True)

  def save(self, request, course_uid, termin_uid, user_uid):
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

    terminbody.points_given = self.cleaned_data['body']
    terminbody.save()
