from django.urls import path
from . import views
from . import admin_views

urlpatterns = [

  path('', views.index, name="index"),
  path('index/', views.index, name="index"),
  #ADMIN----------------------------------------------------------------
  path('admin/rooms/', admin_views.manage_room_view),
  path('admin/rooms/delete/<slug:room_uid>/', admin_views.room_delete),
  path('admin/garants/', admin_views.garant_managment_view),
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
  path('student_evaluation/', views.evaluations_courses_view, name="hodnoceni"),
  path('student_evaluation/<slug:course_uid>/', views.evaluation_term, name="hodnoceni_studentu"),
  path('student_evaluation/<slug:course_uid>/<slug:termin_uid>/', views.evaluation_student, name="hodnoceni_studentu"),
  path('student_evaluation/<slug:course_uid>/<slug:termin_uid>/<slug:user_uid>/', views.evaluation_student_body, name="zadavanie_bodov"),
  path('courses/terms_view/<slug:course_uid>/', views.terms_view, name="terms_view"),
  path('courses/add_lector/<slug:course_uid>/', views.courses_add_lector, name="add_lector"),
  path('courses/create_<slug:termin_type>/<slug:course_uid>/', views.create_term_view),
  path('courses/terms_view/<slug:course_uid>/delete/<slug:termin_uid>/', views.delete_ter, name="delete_ter"),
  path('courses/terms_view/detail/<slug:termin_id>', views.detail_term)
  #path('coures/terms_view/<slug:course_uid>/', ),
  #path('courses/terms_view/<slug:course_uid>/detail/<slug:termin_uid>/', ),
  #path('courses/terms_view/<slug:course_uid>/body/<slug:termin_uid>/', ),

  #path('courses/terms_view/<slug:course_uid>/new/', ),
]


