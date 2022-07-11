from django.db import models
from datetime import date
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .utilities import study_file_parser
from model_utils import FieldTracker
import schedule.utilities.logger as logger
from w3lib.html import replace_entities


class Dicti(models.Model):
    """Словарь справочников"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.CASCADE, blank=True, null=True, related_name="children"
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    # def getidbyconst(self, constname):
    #     return {self.id}

    class Meta:
        verbose_name = "Словарь справочников"
        verbose_name_plural = "Словари справочников"


class DictEduBase(models.Model):
    """Справочник Базы"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True, related_name="childedubase"
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.code} {self.fullname}"

    class Meta:
        verbose_name = "Справочник Базы"
        verbose_name_plural = "Справочники Базы"


class DictObjType(models.Model):
    """СправочникТипОбъекта"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    iscomlpex = models.BooleanField("Составляющий", default=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Тип Объекта"
        verbose_name_plural = "Справочник Типы Объектов"


class DictObjKind(models.Model):
    """СправочникВидОбъекта"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Вид Объекта"
        verbose_name_plural = "Справочник Виды Объектов"


class DictPracticeType(models.Model):
    """СправочникВидыПрактик"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Вид Практики"
        verbose_name_plural = "Справочник Виды Практики"


class DictBlockType(models.Model):
    """СправочникТипБлока"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    isoop = models.BooleanField("ИзООП", default=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.code} {self.fullname}"

    class Meta:
        verbose_name = "Справочник Тип Блока"
        verbose_name_plural = "Справочник Типы Блоков"


class DictEduLvl(models.Model):
    """Справочник УровеньОбразования"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Уровень образования"
        verbose_name_plural = "Справочник Уровни образования"


class DictEduQualifi(models.Model):
    """Справочник Уровень_Образования = квалификация"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    edulevelplan = models.CharField("Вид плана", max_length=200, blank=True, null=True)
    edutype = models.ForeignKey(DictEduLvl, verbose_name="Уровень образования (НПО, СПО, ВПО)", on_delete=models.SET_NULL,
                                blank=True, null=True,  related_name="edu_type")
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Квалификация"
        verbose_name_plural = "Справочник Квалификации"


class DictEduForm(models.Model):
    """Справочник ФормаОбучения"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Форма Обучения"
        verbose_name_plural = "Справочник Формы Обучения"


class DictProgramLvl(models.Model):
    """Справочник ПрограммаПодготовки"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    edulvl = models.ForeignKey(DictEduLvl, verbose_name="Уровень образования (НПО, СПО, ВПО)", on_delete=models.SET_NULL,
                                blank=True, null=True,  related_name="educationlvl")
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Программа Подготовки"
        verbose_name_plural = "Справочник Программы Подготовки"


class DictHoursType(models.Model):
    """СправочникТипаЧасов"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Типа Часов"
        verbose_name_plural = "Справочник Типов Часов"


class DictWorkType(models.Model):
    """Справочник Типы работ"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    iscontact = models.BooleanField("Контактный", default=False)
    isclassroom = models.BooleanField("Аудиторный", default=False)
    hasinter = models.BooleanField("hasinter", default=False)
    hasdistr = models.BooleanField("hasdistr", default=False)
    haspreparing = models.BooleanField("haspreparing", default=False)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Тип работ"
        verbose_name_plural = "Справочник Типы работ"


class DictWorkKind(models.Model):
    """Справочник Виды работ"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    worktype = models.ForeignKey(DictWorkType, verbose_name="Тип работ", on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name="work_type")
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    iscontact = models.BooleanField("Контактный", default=False)
    isclassroom = models.BooleanField("Аудиторный", default=False)
    hasinter = models.BooleanField("hasinter", default=False)
    hasdistr = models.BooleanField("hasdistr", default=False)
    haspreparing = models.BooleanField("haspreparing", default=False)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Вид работ"
        verbose_name_plural = "Справочник Виды работ"


# Нужна ли?
class DictActKind(models.Model):
    """Справочник Виды Деятельности"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    acttype = models.ForeignKey(DictWorkType, verbose_name="Вид деятельности", on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name="act_type")
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Вид деятельности"
        verbose_name_plural = "Справочник Виды деятельности"


class Discipline(models.Model):
    """Справочник Дисциплин"""
    code = models.CharField("Символьный код", max_length=50, blank=True, null=True)
    numcode = models.SmallIntegerField("Числовой код", blank=True, null=True)
    shortname = models.CharField("Краткое наименование", max_length=50, blank=True, null=True)
    fullname = models.CharField("Полное наименование", max_length=4000)
    abbrname = models.CharField("Аббревиатура", max_length=50, blank=True, null=True)
    constname = models.CharField("Константа", max_length=100, blank=True, null=True)
    prefix = models.CharField("Префикс", max_length=50, blank=True, null=True)
    isforeign = models.BooleanField("Иностр.яз", default=False)
    isphiscult = models.BooleanField("Физич.культ.", default=False)
    isstream = models.BooleanField("Поток", default=False)
    priority = models.SmallIntegerField("Приоритет", default=0)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Справочник Дисциплин"
        verbose_name_plural = "Справочник Дисциплин"


class Address(models.Model):
    """Адрес"""
    postcode = models.CharField("Индекс", max_length=10, blank=True, null=True)
    city = models.CharField("Город", max_length=150)
    street = models.CharField("Улица", max_length=50)
    building = models.CharField("Дом, корпус, строение", max_length=20, blank=True, null=True)
    fullName = models.CharField("Полный адрес", max_length=250, blank=True, null=True)
    shortname = models.CharField("Краткий адрес", max_length=250, blank=True, null=True)

    def __str__(self):
        self.fullName = self.city + ' ' + self.street + ' ' + self.building
        return self.fullName

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


class Branch(models.Model):
    """Филиал"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Код", max_length=50, blank=True, null=True)
    shortname = models.CharField("Краткое название", max_length=100, blank=True, null=True)
    fullname = models.CharField("Полное название", max_length=500)
    address = models.ForeignKey(Address, verbose_name="Адрес", on_delete=models.SET_NULL,
                                blank=True, null=True, related_name="branchaddr")
    active = models.BooleanField("Актуальность", default=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"


class Faculty(models.Model):
    """Факультет"""
    code = models.CharField("Код", max_length=50, blank=True, null=True)
    shortname = models.CharField("Краткое название", max_length=100, blank=True, null=True)
    fullname = models.CharField("Полное название", max_length=500)
    branch = models.ForeignKey(Branch, verbose_name="Филиал", on_delete=models.CASCADE, null=True,
                               related_name="facultybranch")
    address = models.ForeignKey(Address, verbose_name="Адрес", on_delete=models.SET_NULL, null=True,
                                related_name="facaddr")
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Факультет"
        verbose_name_plural = "Факультеты"


class Department(models.Model):
    """Кафедра"""
    code = models.CharField("Код", max_length=50, blank=True, null=True)
    shortname = models.CharField("Краткое название", max_length=100,
                                 blank=True, null=True)
    fullname = models.CharField("Полное название", max_length=500)
    faculty = models.ForeignKey(Faculty, verbose_name="Факультет",
                                on_delete=models.SET_NULL, blank=True, null=True,
                                related_name="deptfac")
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Кафедра"
        verbose_name_plural = "Кафедры"


class Room(models.Model):
    """Аудитория"""
    code = models.CharField("Номер", max_length=50)
    floor = models.SmallIntegerField("Этаж", default=1)
    roomclass = models.ForeignKey(Dicti, verbose_name="Тип аудитории", on_delete=models.SET_NULL, null=True,
                                  related_name="roomtype")
    address = models.ForeignKey(Address, verbose_name="Адрес", on_delete=models.SET_NULL, null=True,
                                related_name="roomaddr")
    capacity = models.SmallIntegerField("Вместимость", default=0)
    department = models.ForeignKey(Department, verbose_name="Кафедра", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="roomdept")
    priority = models.SmallIntegerField("Приоритет", default=0)
    isadmiscamp = models.BooleanField("Приемная кампания", default=False)
    active = models.BooleanField("Актуальность", default=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Аудитория"
        verbose_name_plural = "Аудитории"


class Subject(models.Model):
    """Человек"""
    lastname = models.CharField("Фамилия", max_length=100)
    firstname = models.CharField("Имя", max_length=100)
    patronimic = models.CharField("Отчество", max_length=100)
    fullname = models.CharField("Полное имя", max_length=300, blank=True, null=True)
    shortname = models.CharField("Краткое имя", max_length=120, blank=True, null=True)
    subjclass = models.ForeignKey(Dicti, verbose_name="Тип контрагента", on_delete=models.SET_NULL, null=True,
                                  related_name="subjclass")
    academicdegree = models.ForeignKey(Dicti, verbose_name="Ученая степень", on_delete=models.SET_NULL,
                                       related_name="academclass", blank=True, null=True)
    active = models.BooleanField("Актуальность", default=True)
    hiredate = models.DateField("Дата приема", default=date.today)
    releasedate = models.DateField("Дата увольнения", blank=True, null=True)

    def __str__(self):
        self.shortname = self.firstname[:1] + ' ' + self.patronimic[:1] + ' ' + self.lastname
        self.fullname = self.firstname + ' ' + self.patronimic + ' ' + self.lastname
        return self.fullname

    class Meta:
        verbose_name = "Человек"
        verbose_name_plural = "Люди"


class Depteacher(models.Model):
    """Преподаватель на кафедре"""
    department = models.ForeignKey(Department, verbose_name="Кафедра", on_delete=models.CASCADE, null=False,
                                   related_name="depteach")
    subject = models.ForeignKey(Subject, verbose_name="Преподаватель", on_delete=models.CASCADE, null=False,
                                related_name="deptsubj")
    position = models.ForeignKey(Dicti, verbose_name="Должность", on_delete=models.CASCADE, null=False,
                                 related_name="position")
    rate = models.PositiveSmallIntegerField("Ставка", default=0)
    datebeg = models.DateField("Дата начала", default=date.today)
    dateend = models.DateField("Дата окончания", blank=True, null=True)

    def __str__(self):
        return f"{self.department} - {self.subject} - {self.position}"

    class Meta:
        verbose_name = "Преподаватель на кафедре"
        verbose_name_plural = "Преподаватели на кафедрах"


class Discipteacher(models.Model):
    """Дисциплина преподавателя"""
    discipline = models.ForeignKey(Discipline, verbose_name="Дисциплина", on_delete=models.CASCADE, null=False,
                                   related_name="disciplin")
    teacher = models.ForeignKey(Depteacher, verbose_name="Преподаватель", on_delete=models.SET_NULL, null=True,
                                related_name="teachsubj")
    datebeg = models.DateField("Дата начала", default=date.today)
    dateend = models.DateField("Дата окончания", blank=True, null=True)

    def __str__(self):
        return f"{self.discipline} - {self.subject}"

    class Meta:
        verbose_name = "Дисциплина преподавателя"
        verbose_name_plural = "Дисциплины преподавателей"


class EduDirect(models.Model):
    """Направление/Профиль подготовки (из файла "Учебный план" ООП diffgr:)"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Шифр", max_length=50, blank=True, null=True)
    directcode = models.CharField("Код ООП", max_length=50, blank=True, null=True)
    shortname = models.CharField("Краткое название/Префикс", max_length=100, blank=True, null=True)
    fullname = models.CharField("Название", max_length=500)
    edulvl = models.ForeignKey(DictEduLvl, verbose_name="Уровень образования", on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name="education_lvl")
    eduqualifi = models.ForeignKey(DictEduQualifi, verbose_name="Квалификация", on_delete=models.SET_NULL,
                                   blank=True, null=True, related_name="qualification")
    durationyear = models.PositiveSmallIntegerField("СрокЛет", default=1)
    durationmonth = models.PositiveSmallIntegerField("СрокОбученияМесяцев", default=0)
    fgosno = models.CharField("НомерДокумента", max_length=50, blank=True, null=True)
    fgosdate = models.DateField("ДатаДокумента", blank=True, null=True)
    attesttype = models.CharField("ТипГОСа", max_length=50, blank=True, null=True)
    programprep = models.PositiveSmallIntegerField("Программа Подготовки", default=0)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)
    parentextid = models.CharField("КодРодительскогоООП Gosinsp", max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.code} {self.fullname}"

    class Meta:
        verbose_name = "Направление подготовки"
        verbose_name_plural = "Направления подготовки"


class EduProgram(models.Model):
    """Образовательная программа = (из файла "Учебный план" Планы diffgr:id)"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    code = models.CharField("Шифр", max_length=50, blank=True, null=True)
    programcode = models.CharField("Код ООП", max_length=50, blank=True, null=True)
    shortname = models.CharField("Краткое название/Префикс", max_length=100, blank=True, null=True)
    fullname = models.CharField("Название", max_length=500)
    edulvl = models.ForeignKey(DictEduLvl, verbose_name="Уровень образования", on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name="edu_lvl")
    eduqualifi = models.ForeignKey(DictEduQualifi, verbose_name="Квалификация", on_delete=models.SET_NULL,
                                   blank=True, null=True, related_name="qualifi")
    durationyear = models.PositiveSmallIntegerField("СрокЛет", default=1)
    durationmonth = models.PositiveSmallIntegerField("СрокОбученияМесяцев", default=0)
    fgosno = models.CharField("НомерДокумента", max_length=50, blank=True, null=True)
    fgosdate = models.DateField("ДатаДокумента", blank=True, null=True)
    attesttype = models.CharField("ТипГОСа", max_length=50, blank=True, null=True)
    programprep = models.PositiveSmallIntegerField("Программа Подготовки", default=0)
    active = models.BooleanField("Актуальность", default=True)
    extid = models.CharField("код Gosinsp", max_length=100, blank=True, null=True)
    parentextid = models.CharField("КодРодительскогоООП Gosinsp", max_length=100, blank=True, null=True)
    studydirect = models.ForeignKey(EduDirect, verbose_name="Направление/Профиль", on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name="edu_direct")

    def __str__(self):
        return f"{self.code} {self.fullname}"

    class Meta:
        verbose_name = "Образовательная программа"
        verbose_name_plural = "Образовательные программы"


class EduGroup(models.Model):
    """Группа/Подгруппа студентов"""
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    Branch = models.ForeignKey(Branch, verbose_name="Филиал", on_delete=models.SET_NULL,
                               blank=True, null=True, related_name="edugrpbranch", default=0)
    code = models.CharField("Код", max_length=50)
    program = models.ForeignKey(EduProgram, verbose_name="Образовательная программа", on_delete=models.SET_NULL,
                                blank=True, null=True, related_name="grprog", default=0)
    yearadmission = models.PositiveSmallIntegerField("Год приема", default=2021)
    discipline = models.ForeignKey(Discipline, verbose_name="Дисциплина", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="grdiscip")
    quantity = models.PositiveSmallIntegerField("Количество", default=0)
    isforeign = models.BooleanField("Признак иностранная", default=False)
    coursenum = models.PositiveSmallIntegerField("Курс", default=1)
    active = models.BooleanField("Актуальность", default=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Группа/Подгруппа студентов"
        verbose_name_plural = "Группы/Подгруппы студентов"


class Studyfile(models.Model):
    """Файл"""
    fileclass = models.ForeignKey(Dicti, verbose_name="Тип файла", on_delete=models.SET_NULL,
                                  blank=True, null=True, related_name="filetype")
    filestatus = models.ForeignKey(Dicti, verbose_name="Статус обработки файла", on_delete=models.SET_NULL,
                                   blank=True, null=True, related_name="filests")
    title = models.CharField("Название файла", max_length=255, null=True, blank=True)
    filedate = models.DateField("ДатаДокумента", blank=True, null=True)
    courseamount = models.PositiveSmallIntegerField("ЧислоКурсов", default=7)
    semesoncourse = models.PositiveSmallIntegerField("СеместровНаКурсе", default=2)
    sessoncourse = models.PositiveSmallIntegerField("СессийНаКурсе", default=0)
    elemonweek = models.PositiveSmallIntegerField("ЭлементовВНеделе", default=6)
    attesttype = models.CharField("ТипГОСа", max_length=50, blank=True, null=True)
    edulevel = models.ForeignKey(DictEduLvl, verbose_name="Уровень образования", on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name="sfedulvl")
    eduqualifi = models.ForeignKey(DictEduQualifi, verbose_name="Квалификация", on_delete=models.SET_NULL,
                                   blank=True, null=True, related_name="sfqualifi")
    filetext = models.TextField("Текст файла", null=True, blank=True)
    active = models.BooleanField("Актуальность", default=True)
    file = models.FileField(verbose_name="Файл", null=True)

    tracker = FieldTracker()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"


class Studyperiod(models.Model):
    """Учебный год"""
    year = models.PositiveSmallIntegerField("Год", default=2020)
    datebeg = models.DateField("Дата начала", default=date.today)
    dateend = models.DateField("Дата окончания", default=date.today)
    name = models.CharField("Название учебного года", max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Учебный год"
        verbose_name_plural = "Учебные годы"


class Planprog(models.Model):
    """Документ по образоват.программе (Учебный план Планы diffgr:id=). Образоват.программу ищем по КодАктивногоООП"""
    planfile = models.ForeignKey(Studyfile, verbose_name="Файл", on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name="planfile")
    period = models.ForeignKey(Studyperiod, verbose_name="УчебныйГод",
                               on_delete=models.CASCADE, related_name="period", null=True)
    yearstart = models.CharField("ГодНачалаПодготовки", max_length=10, blank=True, null=True)
    eduprog = models.ForeignKey(EduProgram, verbose_name="Образовательная программа", on_delete=models.CASCADE,
                                related_name="studyprog", null=True)
    title = models.TextField("Титул", max_length=500)
    eduform = models.ForeignKey(DictEduForm, verbose_name="Форма обучения", on_delete=models.SET_NULL,
                                blank=True, null=True, related_name="planeduform")
    edulevel = models.ForeignKey(DictEduLvl, verbose_name="Уровень образования", on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name="planedulvl")
    programtype = models.ForeignKey(DictProgramLvl, verbose_name="Тип программы подготовки", on_delete=models.SET_NULL,
                                    blank=True, null=True, related_name="planprogtype")
    qualifi = models.ForeignKey(DictEduQualifi, verbose_name="Квалификация", on_delete=models.SET_NULL,
                                blank=True, null=True, related_name="planskill")
    department = models.ForeignKey(Department, verbose_name="Кафедра", on_delete=models.CASCADE,
                                   related_name="plandept", null=True)
    specializ = models.ForeignKey(Dicti, verbose_name="Специализация", on_delete=models.SET_NULL,
                                  blank=True, null=True, related_name="specializ")
    isdistant = models.BooleanField("Дистанционное", default=False)
    isshort = models.BooleanField("Сокращённое", default=False)
    isforeign = models.BooleanField(" ДляИностранных", default=False)
    ismilitary = models.BooleanField("Военные", default=False)
    militaryspec = models.ForeignKey(Dicti, verbose_name="ВоеннаяСпециальность",
                                     on_delete=models.SET_NULL,
                                     blank=True, null=True, related_name="militaryspec")
    purpose = models.ForeignKey(Dicti, verbose_name="Предназначение", on_delete=models.SET_NULL,
                                blank=True, null=True, related_name="purpose")
    durationyear = models.PositiveSmallIntegerField("СрокОбучения (полных лет)", default=1)
    durationmonth = models.PositiveSmallIntegerField("СрокОбученияМесяцев", default=0)
    courseamount = models.PositiveSmallIntegerField("ЧислоКурсов", default=1)
    sessionamount = models.PositiveSmallIntegerField("ЧислоСессий", default=0)
    semesterpercourse = models.PositiveSmallIntegerField("СеместровНаКурсе", default=2)
    fgosno = models.CharField("НомерФГОС", max_length=50, blank=True, null=True)
    fgosdate = models.DateField("ДатаГОСа", blank=True, null=True)
    attesttype = models.CharField("ТипГОСа", max_length=50, blank=True, null=True)
    weekzet = models.DecimalField("ЗЕТвНеделю", max_digits=6, decimal_places=2, default=0)
    scale = models.DecimalField("Точность", max_digits=6, decimal_places=2, default=0)
    isdviga = models.BooleanField("ДвИГА", default=True)
    isgviga = models.BooleanField("ГвИГА", default=True)
    individ = models.PositiveSmallIntegerField("Индивидуальный", default=0)
    hourscredit = models.DecimalField("ЧасовВКредите", max_digits=6, decimal_places=2, default=0)
    statusonload = models.DecimalField("СтатусВНагрузке", max_digits=6, decimal_places=2, default=0)
    hoursstudy = models.DecimalField("ИзученоКонтЧасов", max_digits=6, decimal_places=2, default=0)
    active = models.BooleanField("Актуальность", default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Учебный план"
        verbose_name_plural = "Учебные планы"


class Planrow(models.Model):
    """Строка ПланыСтроки учебного плана из файла по программе на определенный год"""
    plan = models.ForeignKey(Planprog, verbose_name="План за определенный год", on_delete=models.CASCADE,
                             related_name="rowplan", null=True)
    discipline = models.ForeignKey(Discipline, verbose_name="дисциплина", on_delete=models.CASCADE,
                                   related_name="rowdiscip", null=True)
    disciplinecode = models.CharField("Код дисциплины", max_length=50)
    objtype = models.ForeignKey(DictObjType, verbose_name="Тип объекта", on_delete=models.CASCADE,
                                related_name="rowobjtype", null=True)
    parentobjtype = models.ForeignKey(DictObjType, verbose_name="Родительский тип объекта", on_delete=models.SET_NULL,
                                      blank=True, null=True, related_name="rwparentobjtype")
    objkind = models.ForeignKey(DictObjKind, verbose_name="Вид Объекта", on_delete=models.CASCADE,
                                related_name="rowobjkind", null=True)
    isgym = models.BooleanField("ПризнакФизкультуры", default=False)
    ispractice = models.BooleanField("РассредПрактика", default=False)
    calcnozet = models.BooleanField("СчитатьБезЗЕТ", default=False)
    calcinplan = models.BooleanField("СчитатьВПлане", default=False)
    notcalccontrol = models.BooleanField("НеСчитатьКонтроль", default=False)
    expenseoutdoor = models.BooleanField("ЗаСчетПолевых", default=False)
    complexcredit = models.DecimalField("ТрудоемкостьКредитов", max_digits=6, decimal_places=2, default=0)
    hourszetin = models.DecimalField("ЧасовВЗЕТ", max_digits=6, decimal_places=2, default=0)
    zetfact = models.DecimalField("ЗЕТфакт", max_digits=6, decimal_places=2, default=0)
    hourszetby = models.DecimalField("ЧасовПоЗЕТ", max_digits=6, decimal_places=2, default=0)
    hoursplanby = models.DecimalField("ЧасовПоПлану", max_digits=6, decimal_places=2, default=0)
    hoursstudy = models.DecimalField("ПодлежитИзучениюЧасов", max_digits=6, decimal_places=2, default=0)
    readonly = models.BooleanField("ReadOnly", default=False)
    unnormalpractice = models.BooleanField("НестандартНедПрактики", default=False)
    score = models.DecimalField("Оценка", max_digits=6, decimal_places=2, default=0)
    creditclass = models.PositiveSmallIntegerField("ТипПерезачета", default=0)
    adapt = models.BooleanField("Адаптационная", default=False)
    hoursvarmax = models.DecimalField("ЧасыВарМакс", max_digits=6, decimal_places=2, default=0)
    hoursvaraudit = models.DecimalField("ЧасыВарАуд", max_digits=6, decimal_places=2, default=0)
    hoursauditcredit = models.DecimalField("ПерезачтеноЧасовАуд", max_digits=6, decimal_places=2, default=0)
    notcalcinsumkont = models.BooleanField("NotCalcInSumKont", default=False)
    dvnotequals = models.BooleanField("DVnotEquals", default=False)
    numrow = models.PositiveSmallIntegerField("Номер", default=0)
    ordrow = models.PositiveSmallIntegerField("Порядок", default=0)
    extrowcode = models.IntegerField("Код строки из файла", default=0)
    extdepartmentcode = models.PositiveSmallIntegerField("Код кафедры в файле", default=0)
    extparentrowcode = models.IntegerField("Код родительской записи для вариативных дисциплин", default=0)

    def __str__(self):
        return f"{self.discipline} - {self.disciplinecode}"

    class Meta:
        verbose_name = "Строка ПланыСтроки Учебного плана"
        verbose_name_plural = "Строки ПланыСтроки Учебного плана"


class Planhours(models.Model):
    """Строка ПланыНовыеЧасы по курсам/семестрам учебного плана из файла по программе на определенный год"""
    plan = models.ForeignKey(Planprog, verbose_name="План за определенный год", on_delete=models.CASCADE,
                             related_name="hoursplan", null=True)
    discipline = models.ForeignKey(Discipline, verbose_name="Дисциплина", on_delete=models.CASCADE, default=0,
                                   related_name="phdiscip", null=True)
    parentrow = models.IntegerField("ссылка на строку-объект (дисциплину)-из табл.planrow", default=0)
    activitysubclass = models.ForeignKey(DictWorkKind, verbose_name="Вид работы по справочнику КодВидаРаботы",
                                         on_delete=models.CASCADE, related_name="workkind", null=True)
    activityclass = models.ForeignKey(DictWorkType, verbose_name="Тип объекта", on_delete=models.CASCADE,
                                      related_name="worktype", null=True)
    hoursclass = models.ForeignKey(DictHoursType, verbose_name="Тип Часов", on_delete=models.CASCADE,
                                   related_name="hoursclass", null=True)
    course = models.PositiveSmallIntegerField("Курс", default=0)
    semester = models.PositiveSmallIntegerField("Семестр", default=0)
    session = models.PositiveSmallIntegerField("Сессия", default=0)
    weekamount = models.PositiveSmallIntegerField("Недель", default=0)
    dayamount = models.PositiveSmallIntegerField("Дней", default=0)
    hoursamount = models.DecimalField("Количество", max_digits=6, decimal_places=2, default=0)
    isreattest = models.BooleanField("Переаттестовано", default=False)
    committeeclass = models.PositiveSmallIntegerField("ТипКомиссии", default=0)
    rowcode = models.IntegerField("Код строки файла", default=0)
    parentrowcode = models.IntegerField("код строки-объекта (дисциплину)-из табл.planrow", default=0)

    def __str__(self):
        return str(self.plan)

    class Meta:
        verbose_name = "Строка ПланыНовыеЧасы Учебного плана"
        verbose_name_plural = "Строки ПланыНовыеЧасы Учебного плана"


class Plangraf(models.Model):
    """Строка ПланыГрафикиЯчейки по курсам/семестрам учебного плана из файла по программе на определенный год"""
    plan = models.ForeignKey(Planprog, verbose_name="План за определенный год", on_delete=models.CASCADE,
                             related_name="grafplan", null=True)
    activitykind = models.ForeignKey(DictWorkKind, verbose_name="Вид деятельности", on_delete=models.SET_NULL,
                                  blank=True, null=True, related_name="activ_kind")
    activitykindcode = models.PositiveSmallIntegerField("КодВидаДеятельности GosInsp", default=0)
    weeknum = models.IntegerField("НомерНедели", default=0)
    weekpart = models.IntegerField("НомерЧастиНедели", default=0)
    course = models.PositiveSmallIntegerField("Курс", default=0)
    semester = models.PositiveSmallIntegerField("Семестр", default=0)
    isreattest = models.BooleanField("Переаттестовано", default=False)
    weekpartamount = models.PositiveSmallIntegerField("КоличествоЧастейВНеделе", default=0)
    firstweek = models.PositiveSmallIntegerField("НомерПервойНедели", default=0)
    IsDist = models.BooleanField("IsDist", default=False)
    rowcode = models.IntegerField("Код строки файла", default=0)

    def __str__(self):
        return str(self.plan)

    class Meta:
        verbose_name = "Строка ПланыГрафикиЯчейки Учебного плана"
        verbose_name_plural = "Строки ПланыГрафикиЯчейки Учебного плана"


# Перехват события загрузки файла в БД (ПОСЛЕ самой записи данных в базу)
@receiver(post_save, sender=Studyfile)
def upload_study_file(sender, instance, created, **kwargs):

    if created:
        # Распарсить файл и заполнить инфу о нем самом
        study_file_parser.parse_file_to_db(instance)
        instance.save()

        # Проверить загружался ли уже файл с такими параметрами
        study_file_parser.check_and_update_copy_file(instance)

    # Обновить актуальность для программ, в зависимости от актуальности файла
    study_file_parser.update_actual_info_for_file(instance)

    if instance.tracker.has_changed('active') and not instance.active:
        logger.send_info_to_bot(str(replace_entities("&#10006;")) +
                                " Архивирован файл учебного расписания '" + instance.title + "'")
