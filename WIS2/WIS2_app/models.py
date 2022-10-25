from django.db import models

# Create your models here.


class Course(models.Model):
  class Languages(models.TextChoices):
    ENGLISH = ('ENG', 'English')
    CZECH = ('CZE', 'Czech')
    GERMAN = ('GER', 'German')

  class Kinds(models.TextChoices):
    REQUIRED = ('REQ', 'Required')
    CHOICE = ('CHO', 'Choice')
    FREE = ('FRE', 'Free')

  UID = models.CharField(max_length=5, primary_key=True)
  name = models.CharField(max_length=20)

  kind = models.CharField(max_length=3,
                          choices=Kinds.choices,
                          default=Kinds.REQUIRED)

  description = models.TextField()

  credits = models.PositiveIntegerField(default=4)
  student_limit = models.PositiveIntegerField(default=9999)

  language = models.CharField(max_length=3,
                              choices=Languages.choices,
                              default=Languages.CZECH)

  def __str__(self):
    return self.name


class User(models.Model):
  UID = models.CharField(max_length=8, primary_key=True)
  password = models.CharField(max_length=100)

### Vztazne pro typy userov
# Udelat jen foreign key v course + confirmed
class Garant(models.Model):
  # cascade??
  UserUID = models.ForeignKey(User, on_delete=models.CASCADE)
  CourseUID = models.ForeignKey(Course, on_delete=models.CASCADE)
  confirmed = models.BooleanField(default=False)

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=['UserUID', 'CourseUID'], name='unique garant course ID'
      )
    ]


class Teacher(models.Model):
  UserUID = models.ForeignKey(User, on_delete=models.CASCADE)
  CourseUID = models.ForeignKey(Course, on_delete=models.CASCADE)

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=['UserUID', 'CourseUID'], name='unique teacher course ID'
      )
    ]


class Student(models.Model):
  UserUID = models.ForeignKey(User, on_delete=models.CASCADE)
  CourseUID = models.ForeignKey(Course, on_delete=models.CASCADE)

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=['UserUID', 'CourseUID'], name='unique student course ID'
      )
    ]


class Room(models.Model):
  roomUID = models.CharField(max_length=10, primary_key=True)


# zbavit se czechnglismu
class Termin(models.Model):
  class Kinds(models.TextChoices):
    PERIODIC = ('PER', 'Periodic')
    ONE_TIME = ('ONE', 'OneTime')
  ID = models.UUIDField(primary_key=True)

  CourseUID = models.ForeignKey(Course, on_delete=models.CASCADE)

  RoomUID = models.ForeignKey(Room, on_delete=models.DO_NOTHING)
  max_points = models.PositiveIntegerField()

  description = models.CharField(max_length=2000)
  kind = models.CharField(max_length=3, choices=Kinds.choices, default=Kinds.ONE_TIME)

# specializuju at nemusime mit ruzne vztazne pro period a single terminy
class TerminPeriod(models.Model):
  TerminID = models.ForeignKey(Termin, on_delete=models.CASCADE, primary_key=True)

  start = models.DateTimeField()
  repeats = models.PositiveIntegerField()
  periodicity = models.PositiveIntegerField()


class TerminSingle(models.Model):
  TerminID = models.ForeignKey(Termin, on_delete=models.CASCADE, primary_key=True)

  date = models.DateTimeField()

### Vztazna na BODY
class Termin2Body(models.Model):
  TerminUID = models.ForeignKey(Termin, on_delete=models.CASCADE)
  StudentUID = models.ForeignKey(Student, on_delete=models.CASCADE)
  TeacherUID = models.ForeignKey(Teacher, on_delete=models.CASCADE)

  points_given = models.PositiveIntegerField()

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=['TerminUID', 'StudentUID', 'TeacherUID'], name='unique termin,student,teacher UID'
      )
    ]