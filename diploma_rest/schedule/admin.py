from django.contrib import admin

from .models import Dicti, DictEduBase, DictObjType, DictObjKind, DictPracticeType, DictBlockType, DictEduLvl, \
    DictEduQualifi, DictEduForm, DictProgramLvl, DictHoursType, DictWorkType, DictWorkKind, DictActKind, \
    Discipline, Address, Branch, Faculty, Department, Room, Subject, Depteacher, Discipteacher, EduProgram, EduGroup, \
    Studyfile, Studyperiod, Planprog, Planrow, Planhours, Plangraf, EduDirect


admin.site.register(Dicti)
admin.site.register(DictEduBase)
admin.site.register(DictObjType)
admin.site.register(DictObjKind)
admin.site.register(DictPracticeType)
admin.site.register(DictBlockType)
admin.site.register(DictEduLvl)
admin.site.register(DictEduQualifi)
admin.site.register(DictEduForm)
admin.site.register(DictProgramLvl)
admin.site.register(DictHoursType)
admin.site.register(DictWorkType)
admin.site.register(DictWorkKind)
admin.site.register(DictActKind)
admin.site.register(Discipline)
admin.site.register(Address)
admin.site.register(Branch)
admin.site.register(Faculty)
admin.site.register(Department)
admin.site.register(Room)
admin.site.register(Subject)
admin.site.register(Depteacher)
admin.site.register(Discipteacher)
admin.site.register(EduDirect)
admin.site.register(EduProgram)
admin.site.register(EduGroup)
admin.site.register(Studyfile)
admin.site.register(Studyperiod)
admin.site.register(Planprog)
admin.site.register(Planrow)
admin.site.register(Planhours)
admin.site.register(Plangraf)
