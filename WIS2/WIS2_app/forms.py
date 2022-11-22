from django import forms
from .models import Course
from .validators import validate_is_positive, validate_alphanumeric_strings

COURSE_KINDS = [
    ('REQ', 'Required'),
    ('CHO', 'Choice'),
    ('FRE', 'Free'),
]

class CreateCourseForm(forms.Form):
  uid = forms.CharField(label="Short name", max_length=5, required=True)
  name = forms.CharField(label="Name", max_length=20, required=True)

  kind = forms.CharField(label="Course type:", required=True,
                         widget=forms.Select(choices=COURSE_KINDS))

  credit = forms.IntegerField(label="Credits", required=True,
                              validators=[validate_is_positive])

  students = forms.IntegerField(label="Student limit", required=True,
                                validators=[validate_is_positive])

  lang = forms.CharField(label="Language", max_length=3, required=True)

  desc = forms.CharField(label="description", required=True,
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