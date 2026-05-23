from django.contrib import admin
from .models import Teacher, Subject, Classroom, Group, TimetableCard, LessonRecord, MonthlyReport, ReportDeadline, Department

admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Classroom)
admin.site.register(Group)
admin.site.register(TimetableCard)
admin.site.register(LessonRecord)
admin.site.register(MonthlyReport)
admin.site.register(ReportDeadline)
admin.site.register(Department)