from django import forms
from .models import *
from .validators import validate_is_positive, validate_alphanumeric_strings

COURSE_KINDS = [
    ('REQ', 'Required'),
    ('CHO', 'Choice'),
    ('FRE', 'Free'),
]

TERMIN_KINDS = [
    ('PER', 'Periodic'),
    ('ONE', 'OneTime'),
]
TERMIN_TYPE =[
    ('PLEC', 'Practice lecture'),
    ('LEC', 'Lecture'),
    ('EXM', "Exam"),
    ('PRJ', "Project"),
]

class CreateCourseForm(forms.Form):
    uid = forms.CharField(label="Short name", max_length=5, required=True)
    name = forms.CharField(label="Name", max_length=40, required=True)

    kind = forms.CharField(label="Course type:", required=True,
                           widget=forms.Select(choices=Course.Kinds.choices))

    credit = forms.IntegerField(label="Credits", required=True,
                                validators=[validate_is_positive], min_value=1, max_value=30)

    students = forms.IntegerField(label="Student limit", required=True,
                                  validators=[validate_is_positive], min_value=1, max_value=999)

    lang = forms.CharField(label="Language", max_length=3, required=True, widget=forms.Select(choices=
                                                                                              Course.Languages.choices))

    desc = forms.CharField(label="Description", required=True,
                           widget=forms.Textarea)

    def save(self):
        course = Course()
        course.UID = self.cleaned_data['uid']
        course.name = self.cleaned_data['name']
        course.kind = self.cleaned_data['kind']
        course.credits = self.cleaned_data['credit']
        course.student_limit = self.cleaned_data['students']
        course.language = self.cleaned_data['lang']
        course.description = self.cleaned_data['desc']
        course.save()


class CreateRoomForm(forms.Form):
    uid = forms.CharField(label="Room number", max_length=10, required=True)

    def save(self):
        print("got here")
        room = Room()
        room.roomUID = self.cleaned_data['uid']
        room.save()


class CreateTerminForm(forms.Form):
    #courseID = forms.CharField(label="courseid", required=True)   #forms.CharField(label="Course:", required=True, widget=forms.Select(choices=Course.objects.all()))

    room = forms.CharField(label="Room number:", required=True)
    points = forms.IntegerField(label="Maximum points:", required=True, min_value=0)
    kind = forms.CharField(label="Periodic?: ", required=True,
                           widget=forms.Select(choices=TERMIN_KINDS))
    desc = forms.CharField(label="Description", required=False,
                           widget=forms.Textarea)
    kind_type = forms.CharField(label="TYPE", required=True, widget=forms.Select(choices=TERMIN_TYPE))
    repeats = forms.IntegerField(label="repeats", required=False, min_value=0)

    periodicity = forms.IntegerField(label="periodicity", required=False, min_value=0)

    date = forms.DateTimeField(label="date", required=True)

    def save(self, str, course_uid):
        termin = Termin()
        termin.CourseUID = Course.objects.get(UID__exact=course_uid)
        termin.RoomUID = Room.objects.get(roomUID__exact=self.cleaned_data['room'])
        termin.max_points = self.cleaned_data['points']
        termin.kind = self.cleaned_data['kind']
        termin.description = self.cleaned_data['desc']
        termin.save()
        if str == "periodic":
            terminperiodic = TerminPeriod()
            terminperiodic.kind = self.cleaned_data['kind_type']
            terminperiodic.TerminID = Termin.objects.get(ID__exact=termin.ID)
            terminperiodic.start = self.cleaned_data['date']
            terminperiodic.repeats = self.cleaned_data['repeats']
            terminperiodic.periodicity= self.cleaned_data['periodicity']
            terminperiodic.save()
        else:
            terminsingle = TerminSingle()
            terminsingle.TerminID = Termin.objects.get(ID__exact=termin.ID)
            terminsingle.kind = self.cleaned_data['kind_type']
            terminsingle.date = self.cleaned_data['date']
            terminsingle.save()