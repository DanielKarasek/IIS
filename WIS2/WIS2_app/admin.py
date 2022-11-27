from django.contrib import admin
from .models import Garant, Course, Teacher, Student, Termin, TerminPeriod, TerminSingle, Termin2Body

admin.site.register(Garant)
admin.site.register(Course)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Termin)
admin.site.register(TerminPeriod)
admin.site.register(TerminSingle)
admin.site.register(Termin2Body)

# Register your models here.
