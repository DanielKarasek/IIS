from django.urls import path
from . import views
from . import admin_views

urlpatterns = [

  path('', views.index, name="index"),
  path('index/', views.index, name="index"),
  #ADMIN----------------------------------------------------------------
  path('admin/rooms/', admin_views.room),
  path('admin/rooms/delete/<slug:room_uid>/', admin_views.room_delete),
  path('admin/garants/', admin_views.garants),
  path('admin/garants/<slug:course_uid>/', admin_views.garants_change_confirmed),
  #USER-----------------------------------------------------------------
  path('user/', views.user, name="user"),
  path('user/change_password/', views.user_change_password, name="delete_password"),
  path('user/delete/', views.user_delete, name="delete_password"),
  #COURSE---------------------------------------------------------------
  path('courses/', views.courses, name="courses"),
  path('my_courses/', views.my_courses, name="my_courses"),
  path('create_course/', views.courses_create, name="create_course"),
  path('courses/join/<slug:course_uid>/', views.courses_join),
  path('courses/leave/<slug:course_uid>/', views.courses_leave),
  path('courses/delete/<slug:course_uid>/', views.courses_delete),
  path('courses/detail/<slug:course_uid>/', views.courses_detail, name="courses_detail"),
  path('my_courses/detail/<slug:course_uid>/', views.courses_detail, name="courses_detail"),
  #TERMIN---------------------------------------------------------------
  path('student_evaluation/', views.evaluation, name="hodnoceni"),
  path('student_evaluation/<slug:course_uid>/', views.evaluation_termin, name="hodnoceni_studentu"),
  path('student_evaluation/<slug:course_uid>/<slug:termin_uid>/', views.evaluation_student, name="hodnoceni_studentu"),
  path('student_evaluation/<slug:course_uid>/<slug:termin_uid>/<slug:user_uid>/', views.evaluation_student_body, name="zadavanie_bodov"),
  path('courses/termins/<slug:course_uid>/', views.termins, name="termins"),
  path('courses/create_<slug:termin_type>/<slug:course_uid>/', views.create_termin),
  path('courses/termins/<slug:course_uid>/delete/<slug:termin_uid>/', views.delete_termin, name="delete_termin"),

  #path('coures/termins/<slug:course_uid>/', ),
  #path('courses/termins/<slug:course_uid>/detail/<slug:termin_uid>/', ),
  #path('courses/termins/<slug:course_uid>/body/<slug:termin_uid>/', ),

  #path('courses/termins/<slug:course_uid>/new/', ),
]


