from django import forms
from .validators import validate_alphanumeric_strings


class CreateCourseForm(forms.Form):
  UID = forms.CharField(label="UID",
                        max_length=5,
                        validators=[validate_alphanumeric_strings],
                        required=True)
  name = forms.CharField(label="Name", max_length=20, required=True)


