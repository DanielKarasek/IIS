from django.urls import path
from . import views
from . import admin_views


urlpatterns = [

  path('', views.index, name="index"),
  #ADMIN----------------------------------------------------------------
  path('admin/rooms/', admin_views.room),
  path('admin/rooms/delete/<slug:room_uid>/', admin_views.room_delete),
  path('admin/garants/', admin_views.garants),
  path('admin/garants/<slug:course_uid>/', admin_views.garants_change_confirmed),
  #USER-----------------------------------------------------------------
  path('user/', views.user, name="user"),
  #COURSE---------------------------------------------------------------
  path('courses/', views.courses, name="courses"),
  path('create_course/', views.courses_create, name="create_course"),
  path('courses/join/<slug:course_uid>/', views.courses_join),
  path('courses/leave/<slug:course_uid>/', views.courses_leave),
  path('courses/detail/<slug:course_uid>/', views.courses_detail, name="courses_detail"),
  #TERMIN---------------------------------------------------------------
  path('courses/termins/', views.termins),
  #path('coures/termins/<slug:course_uid>/', ),
  #path('courses/termins/<slug:course_uid>/detail/<slug:termin_uid>/', ),
  #path('courses/termins/<slug:course_uid>/body/<slug:termin_uid>/', ),

  #path('courses/termins/<slug:course_uid>/new/', ),
  #path('courses/termins/<slug:course_uid>/delete/<slug:termin_uid>/', ),
]
