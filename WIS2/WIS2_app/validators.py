from django.core.exceptions import ValidationError


def validate_alphanumeric_strings(value: str,
                                  numeric_start_valid: bool = False):
  """ Validates strings so they contain only alphanumeric chars. """
  if not numeric_start_valid:
    if not value[0].isalpha():
      raise ValidationError(f"{value} doesn't start with alpha character")
  if not str.isalnum(value):
    raise ValidationError(f"{value} isn't alphanumeric string")

