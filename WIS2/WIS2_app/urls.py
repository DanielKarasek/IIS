from django.urls import path
from . import views
from . import admin_views


urlpatterns = [

  path('', views.index, name="index"),
  path('admin/rooms/', admin_views.room),
  path('admin/rooms/<int:id>/', admin_views.room_delete),
  path('user/', views.user, name="user"),
  path('courses/', views.courses, name="courses"),

]
