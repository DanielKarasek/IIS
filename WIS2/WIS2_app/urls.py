from django.urls import path
from . import views


urlpatterns = [

  path('', views.index, name="index"),
  path('user', views.user, name="user"),
  path('courses', views.courses, name="courses"),
  path('<str:name>', views.index2, name="index2"),
]
