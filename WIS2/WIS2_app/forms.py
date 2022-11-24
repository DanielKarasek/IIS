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
    courseID = ''

    room = forms.CharField(label="Room number:", required=False)
    points = forms.IntegerField(label="Maximum points:", required=True, min_value=0)
    kind = forms.CharField(label="Periodic?: ", required=True,
                           widget=forms.Select(choices=TERMIN_KINDS))
    desc = forms.CharField(label="Description", required=False,
                           widget=forms.Textarea)

    def save(self):
        termin = Termin()
        termin.CourseUID = self.courseID
        termin.RoomUID = self.cleaned_data['room']
        termin.max_points = self.cleaned_data['points']
        termin.kind = self.cleaned_data['kind']
        termin.description = self.cleaned_data['desc']
        termin.save()