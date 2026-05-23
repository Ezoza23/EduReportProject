from django.contrib import admin
from django.urls import path
from timetable import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('timetable/', views.timetable_view, name='timetable'),
    path('logout/', views.logout_view, name='logout'),
    path('mark-lesson/', views.mark_lesson, name='mark_lesson'),
    path('submit-report/', views.submit_report, name='submit_report'),
    path('dean/', views.dean_dashboard, name='dean_dashboard'),
    path('set-deadline/', views.set_deadline, name='set_deadline'),
    path('dean/export/', views.export_dean_excel, name='export_dean_excel'),
]