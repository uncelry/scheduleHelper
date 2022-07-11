from bs4 import BeautifulSoup
from datetime import datetime
import schedule.models as models
import schedule.utilities.logger as logger
from w3lib.html import replace_entities


def bool_convert(string):
    """
    Функция, конвертирующая строку с логической информацией в логический тип
    :param string: строка
    :return: логический тип данных
    """

    # Получаем строку и сравниваем
    if (string == 'true') or (string == 'True'):
        return True
    return False


def get_from_xml(ret_type, xml_obj, selector):
    try:
        return ret_type(xml_obj[selector])
    except KeyError:
        return None


def parse_val_into_field(ret_type, xml_obj, selector, instance, model_filed_name):
    ret = get_from_xml(ret_type, xml_obj, selector)

    if ret is None:
        return instance._meta.get_field(model_filed_name).get_default()

    if ret_type == str:
        return ret[:instance._meta.get_field(model_filed_name).max_length]

    return ret


def find_branch_from_xml(soup_obj, selector):
    try:
        return soup_obj.find(selector)
    except KeyError:
        return None


def find_branch_from_xml_all(soup_obj, selector):
    try:
        return soup_obj.findAll(selector)
    except KeyError:
        return None


def study_file_info_to_model(bs_file_info, instance, file_content):
    """
    Процедура, которая парсит данные о файле в БД
    :param bs_file_info: файл для парсинга в формате BeautifulSoup
    :param instance: запись в БД, куда нужно внести данные
    :param file_content: содержимое файла строкой
    """

    # Сперва, получаем данные о файле
    doc_info = find_branch_from_xml(bs_file_info, 'Документ')
    if not doc_info:
        return

    # Записываем данные
    try:
        instance.fileclass = models.Dicti.objects.filter(constname="УчебныйПлан").first()
    except ValueError:
        pass

    try:
        instance.filestatus = models.Dicti.objects.filter(constname="Загружен").first()
    except ValueError:
        pass

    instance.title = parse_val_into_field(str, doc_info, 'LastName', instance, 'title')

    try:
        instance.filedate = datetime.strptime(doc_info['LastWrite'], '%d.%m.%Y').date()
    except:
        instance.filedate = None

    instance.courseamount = parse_val_into_field(int, doc_info, 'ЧислоКурсов', instance, 'courseamount')

    instance.semesoncourse = parse_val_into_field(int, doc_info, 'СеместровНаКурсе', instance, 'semesoncourse')

    instance.sessoncourse = parse_val_into_field(int, doc_info, 'СессийНаКурсе', instance, 'sessoncourse')

    instance.elemonweek = parse_val_into_field(int, doc_info, 'ЭлементовВНеделе', instance, 'elemonweek')

    instance.attesttype = parse_val_into_field(str, doc_info, 'ТипГОСа', instance, 'attesttype')

    instance.filetext = str(file_content)

    instance.save()


def study_file_additional_to_model(bs_file_info, instance):
    """
    Процедура, которая парсит дополнительные данные о файле в БД
    :param bs_file_info: файл для парсинга в формате BeautifulSoup
    :param instance: запись в БД, куда нужно внести данные
    """

    # Сперва, получаем данные о файле
    doc_info = find_branch_from_xml(bs_file_info, 'Документ')
    if not doc_info:
        return

    try:
        instance.edulevel = models.DictEduLvl.objects.filter(code=doc_info['КодУровняОбразования']).first()
    except ValueError:
        pass

    try:
        instance.eduqualifi = this_file_oop = models.Planprog.objects.filter(planfile=instance).first().qualifi
    except ValueError:
        pass

    instance.save()


def branches_to_model(bs_file):
    """
    Процедура, которая парсит данные о филиале в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию о филиалах
    branches = find_branch_from_xml_all(bs_file, 'Филиалы')
    if not branches:
        return

    # В цикле проходимся по всем филиалам
    for item in branches:

        tmp_branch = models.Branch()

        if not bool_convert(item['Головное_учреждение']):
            tmp_branch.parent = models.Branch.objects.filter(parent__isnull=True).distinct().first()

        tmp_branch.code = parse_val_into_field(str, item, 'Код_филиала', tmp_branch, 'code')

        tmp_branch.shortname = parse_val_into_field(str, item, 'Краткое_Название', tmp_branch, 'shortname')

        tmp_branch.fullname = parse_val_into_field(str, item, 'Полное_название', tmp_branch, 'fullname')

        if not models.Branch.objects.filter(parent=tmp_branch.parent,
                                            code=tmp_branch.code,
                                            shortname=tmp_branch.shortname,
                                            fullname=tmp_branch.fullname):
            tmp_branch.save()


def faculty_to_model(bs_file):
    """
    Процедура, которая парсит данные о факультете в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию о факультете
    faculty = find_branch_from_xml_all(bs_file, 'Факультеты')
    if not faculty:
        return

    # В цикле проходимся по всем факультетам
    for item in faculty:

        tmp_faculty = models.Faculty()

        tmp_faculty.code = parse_val_into_field(str, item, 'Код', tmp_faculty, 'code')

        tmp_faculty.shortname = parse_val_into_field(str, item, 'Сокращение', tmp_faculty, 'shortname')

        tmp_faculty.fullname = parse_val_into_field(str, item, 'Факультет', tmp_faculty, 'fullname')

        try:
            tmp_faculty.branch = models.Branch.objects.filter(code=item['Код_филиала']).first()
            tmp_faculty.address = models.Branch.objects.filter(code=item['Код_филиала']).first().address
        except ValueError:
            pass

        tmp_faculty.extid = parse_val_into_field(str, item, 'Код', tmp_faculty, 'extid')

        if not models.Faculty.objects.filter(code=tmp_faculty.code,
                                             shortname=tmp_faculty.shortname,
                                             fullname=tmp_faculty.fullname,
                                             branch=tmp_faculty.branch,
                                             address=tmp_faculty.address,
                                             extid=tmp_faculty.extid):
            tmp_faculty.save()


def degree_level_to_model(bs_file):
    """
    Процедура, которая парсит данные о уровне образования в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'УровеньОбразования')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_dict_edu = models.DictEduLvl()

        tmp_dict_edu.code = parse_val_into_field(str, item, 'Код', tmp_dict_edu, 'code')

        tmp_dict_edu.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_edu, 'numcode')

        tmp_dict_edu.shortname = parse_val_into_field(str, item, 'Уровень', tmp_dict_edu, 'shortname')

        tmp_dict_edu.fullname = parse_val_into_field(str, item, 'Уровень', tmp_dict_edu, 'fullname')

        tmp_dict_edu.abbrname = parse_val_into_field(str, item, 'Уровень', tmp_dict_edu, 'abbrname')

        tmp_dict_edu.constname = parse_val_into_field(str, item, 'Уровень', tmp_dict_edu, 'constname')

        tmp_dict_edu.prefix = parse_val_into_field(str, item, 'Префикс', tmp_dict_edu, 'prefix')

        tmp_dict_edu.extid = parse_val_into_field(str, item, 'Код', tmp_dict_edu, 'extid')

        if not models.DictEduLvl.objects.filter(code=tmp_dict_edu.code,
                                                numcode=tmp_dict_edu.numcode,
                                                shortname=tmp_dict_edu.shortname,
                                                fullname=tmp_dict_edu.fullname,
                                                abbrname=tmp_dict_edu.abbrname,
                                                constname=tmp_dict_edu.constname,
                                                prefix=tmp_dict_edu.prefix,
                                                extid=tmp_dict_edu.extid):
            tmp_dict_edu.save()


def program_info_to_model(bs_file):
    """
    Процедура, которая парсит данные о программе подготовки в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию о программе
    program = find_branch_from_xml_all(bs_file, 'ПрограммаПодготовки')
    if not program:
        return

    # В цикле проходимся по всем программам
    for item in program:

        tmp_dict_program_lvl = models.DictProgramLvl()

        tmp_dict_program_lvl.code = parse_val_into_field(str, item, 'Код', tmp_dict_program_lvl, 'code')

        tmp_dict_program_lvl.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_program_lvl, 'numcode')

        tmp_dict_program_lvl.shortname = parse_val_into_field(str, item, 'Наименование', tmp_dict_program_lvl,
                                                              'shortname')

        tmp_dict_program_lvl.fullname = parse_val_into_field(str, item, 'Наименование', tmp_dict_program_lvl,
                                                             'fullname')

        tmp_dict_program_lvl.abbrname = parse_val_into_field(str, item, 'Наименование', tmp_dict_program_lvl,
                                                             'abbrname')

        tmp_dict_program_lvl.constname = parse_val_into_field(str, item, 'Наименование', tmp_dict_program_lvl,
                                                              'constname')

        tmp_dict_program_lvl.prefix = parse_val_into_field(str, item, 'Префикс', tmp_dict_program_lvl, 'prefix')

        try:
            tmp_dict_program_lvl.edulvl = models.DictEduLvl.objects.filter(code=str(item['Уровень'])).first()
        except ValueError:
            pass

        tmp_dict_program_lvl.extid = parse_val_into_field(str, item, 'Код', tmp_dict_program_lvl, 'extid')

        if not models.DictProgramLvl.objects.filter(code=tmp_dict_program_lvl.code,
                                                    numcode=tmp_dict_program_lvl.numcode,
                                                    shortname=tmp_dict_program_lvl.shortname,
                                                    fullname=tmp_dict_program_lvl.fullname,
                                                    abbrname=tmp_dict_program_lvl.abbrname,
                                                    constname=tmp_dict_program_lvl.constname,
                                                    prefix=tmp_dict_program_lvl.prefix,
                                                    edulvl=tmp_dict_program_lvl.edulvl,
                                                    extid=tmp_dict_program_lvl.extid):
            tmp_dict_program_lvl.save()


def reference_base_to_model(bs_file):
    """
    Процедура, которая парсит данные о справочник базы в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию о справочнике базы
    info = find_branch_from_xml_all(bs_file, 'СправочникБазы')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_dict_edu_base = models.DictEduBase()

        tmp_dict_edu_base.code = parse_val_into_field(str, item, 'Код', tmp_dict_edu_base, 'code')

        tmp_dict_edu_base.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_edu_base, 'numcode')

        tmp_dict_edu_base.shortname = parse_val_into_field(str, item, 'Наименование', tmp_dict_edu_base, 'shortname')

        tmp_dict_edu_base.fullname = parse_val_into_field(str, item, 'Наименование', tmp_dict_edu_base, 'fullname')

        tmp_dict_edu_base.abbrname = parse_val_into_field(str, item, 'Наименование', tmp_dict_edu_base, 'abbrname')

        tmp_dict_edu_base.constname = parse_val_into_field(str, item, 'Наименование', tmp_dict_edu_base, 'constname')

        tmp_dict_edu_base.prefix = parse_val_into_field(str, item, 'Префикс', tmp_dict_edu_base, 'prefix')

        tmp_dict_edu_base.extid = parse_val_into_field(str, item, 'Код', tmp_dict_edu_base, 'extid')

        if not models.DictEduBase.objects.filter(code=tmp_dict_edu_base.code,
                                                 numcode=tmp_dict_edu_base.numcode,
                                                 shortname=tmp_dict_edu_base.shortname,
                                                 fullname=tmp_dict_edu_base.fullname,
                                                 abbrname=tmp_dict_edu_base.abbrname,
                                                 constname=tmp_dict_edu_base.constname,
                                                 prefix=tmp_dict_edu_base.prefix,
                                                 extid=tmp_dict_edu_base.extid):
            tmp_dict_edu_base.save()


def object_type_to_model(bs_file):
    """
    Процедура, которая парсит данные о справочник виде объекта в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'СправочникВидОбъекта')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_dict_obj_kind = models.DictObjKind()

        tmp_dict_obj_kind.code = parse_val_into_field(str, item, 'Код', tmp_dict_obj_kind, 'code')

        tmp_dict_obj_kind.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_obj_kind, 'numcode')

        tmp_dict_obj_kind.shortname = parse_val_into_field(str, item, 'Наименование', tmp_dict_obj_kind, 'shortname')

        tmp_dict_obj_kind.fullname = parse_val_into_field(str, item, 'Наименование', tmp_dict_obj_kind, 'fullname')

        tmp_dict_obj_kind.abbrname = parse_val_into_field(str, item, 'Наименование', tmp_dict_obj_kind, 'abbrname')

        tmp_dict_obj_kind.constname = parse_val_into_field(str, item, 'Наименование', tmp_dict_obj_kind, 'constname')

        tmp_dict_obj_kind.prefix = None

        tmp_dict_obj_kind.extid = parse_val_into_field(str, item, 'Код', tmp_dict_obj_kind, 'extid')

        if not models.DictObjKind.objects.filter(code=tmp_dict_obj_kind.code,
                                                 numcode=tmp_dict_obj_kind.numcode,
                                                 shortname=tmp_dict_obj_kind.shortname,
                                                 fullname=tmp_dict_obj_kind.fullname,
                                                 abbrname=tmp_dict_obj_kind.abbrname,
                                                 constname=tmp_dict_obj_kind.constname,
                                                 prefix=tmp_dict_obj_kind.prefix,
                                                 extid=tmp_dict_obj_kind.extid):
            tmp_dict_obj_kind.save()


def practice_type_to_model(bs_file):
    """
    Процедура, которая парсит данные о практике в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'СправочникВидыПрактик')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_dict_practice_type = models.DictPracticeType()

        tmp_dict_practice_type.code = parse_val_into_field(str, item, 'Код', tmp_dict_practice_type, 'code')

        tmp_dict_practice_type.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_practice_type, 'numcode')

        tmp_dict_practice_type.shortname = parse_val_into_field(str, item, 'Наименование', tmp_dict_practice_type,
                                                                'shortname')

        tmp_dict_practice_type.fullname = parse_val_into_field(str, item, 'Наименование', tmp_dict_practice_type,
                                                               'fullname')

        tmp_dict_practice_type.abbrname = parse_val_into_field(str, item, 'Наименование', tmp_dict_practice_type,
                                                               'abbrname')

        tmp_dict_practice_type.constname = parse_val_into_field(str, item, 'Наименование', tmp_dict_practice_type,
                                                                'constname')

        tmp_dict_practice_type.prefix = parse_val_into_field(str, item, 'Префикс', tmp_dict_practice_type, 'prefix')

        tmp_dict_practice_type.extid = parse_val_into_field(str, item, 'Код', tmp_dict_practice_type, 'extid')

        if not models.DictPracticeType.objects.filter(code=tmp_dict_practice_type.code,
                                                      numcode=tmp_dict_practice_type.numcode,
                                                      shortname=tmp_dict_practice_type.shortname,
                                                      fullname=tmp_dict_practice_type.fullname,
                                                      abbrname=tmp_dict_practice_type.abbrname,
                                                      constname=tmp_dict_practice_type.constname,
                                                      prefix=tmp_dict_practice_type.prefix,
                                                      extid=tmp_dict_practice_type.extid):
            tmp_dict_practice_type.save()


def hours_type_to_model(bs_file):
    """
    Процедура, которая парсит данные о типе часов в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'СправочникТипаЧасов')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_dict_hours_type = models.DictHoursType()

        tmp_dict_hours_type.code = parse_val_into_field(str, item, 'Код', tmp_dict_hours_type, 'code')

        tmp_dict_hours_type.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_hours_type, 'numcode')

        tmp_dict_hours_type.shortname = parse_val_into_field(str, item, 'Наименование', tmp_dict_hours_type,
                                                             'shortname')

        tmp_dict_hours_type.fullname = parse_val_into_field(str, item, 'Наименование', tmp_dict_hours_type, 'fullname')

        tmp_dict_hours_type.abbrname = parse_val_into_field(str, item, 'Наименование', tmp_dict_hours_type, 'abbrname')

        tmp_dict_hours_type.constname = parse_val_into_field(str, item, 'Наименование', tmp_dict_hours_type,
                                                             'constname')

        tmp_dict_hours_type.prefix = None

        tmp_dict_hours_type.extid = parse_val_into_field(str, item, 'Код', tmp_dict_hours_type, 'extid')

        if not models.DictHoursType.objects.filter(code=tmp_dict_hours_type.code,
                                                   numcode=tmp_dict_hours_type.numcode,
                                                   shortname=tmp_dict_hours_type.shortname,
                                                   fullname=tmp_dict_hours_type.fullname,
                                                   abbrname=tmp_dict_hours_type.abbrname,
                                                   constname=tmp_dict_hours_type.constname,
                                                   prefix=tmp_dict_hours_type.prefix,
                                                   extid=tmp_dict_hours_type.extid):
            tmp_dict_hours_type.save()


def block_type_to_model(bs_file):
    """
    Процедура, которая парсит данные о типе блока в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'СправочникТипБлока')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_dict_block_type = models.DictBlockType()

        tmp_dict_block_type.code = parse_val_into_field(str, item, 'Код', tmp_dict_block_type, 'code')

        tmp_dict_block_type.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_block_type, 'numcode')

        tmp_dict_block_type.shortname = parse_val_into_field(str, item, 'Название', tmp_dict_block_type, 'shortname')

        tmp_dict_block_type.fullname = parse_val_into_field(str, item, 'Название', tmp_dict_block_type, 'fullname')

        tmp_dict_block_type.abbrname = parse_val_into_field(str, item, 'Название', tmp_dict_block_type, 'abbrname')

        tmp_dict_block_type.constname = parse_val_into_field(str, item, 'Название', tmp_dict_block_type, 'constname')

        tmp_dict_block_type.prefix = None

        tmp_dict_block_type.isoop = parse_val_into_field(bool_convert, item, 'ИзООП', tmp_dict_block_type, 'isoop')

        tmp_dict_block_type.extid = parse_val_into_field(str, item, 'Код', tmp_dict_block_type, 'extid')

        if not models.DictBlockType.objects.filter(code=tmp_dict_block_type.code,
                                                   numcode=tmp_dict_block_type.numcode,
                                                   shortname=tmp_dict_block_type.shortname,
                                                   fullname=tmp_dict_block_type.fullname,
                                                   abbrname=tmp_dict_block_type.abbrname,
                                                   constname=tmp_dict_block_type.constname,
                                                   prefix=tmp_dict_block_type.prefix,
                                                   isoop=tmp_dict_block_type.isoop,
                                                   extid=tmp_dict_block_type.extid):
            tmp_dict_block_type.save()


def reference_object_type_to_model(bs_file):
    """
    Процедура, которая парсит данные о справочнике типа объекта в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'СправочникТипОбъекта')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_dict_obj_type = models.DictObjType()

        tmp_dict_obj_type.code = parse_val_into_field(str, item, 'Код', tmp_dict_obj_type, 'code')

        tmp_dict_obj_type.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_obj_type, 'numcode')

        tmp_dict_obj_type.shortname = parse_val_into_field(str, item, 'Название', tmp_dict_obj_type, 'shortname')

        tmp_dict_obj_type.fullname = parse_val_into_field(str, item, 'Название', tmp_dict_obj_type, 'fullname')

        tmp_dict_obj_type.abbrname = parse_val_into_field(str, item, 'Название', tmp_dict_obj_type, 'abbrname')

        tmp_dict_obj_type.constname = parse_val_into_field(str, item, 'Название', tmp_dict_obj_type, 'constname')

        tmp_dict_obj_type.prefix = None

        # tmp_dict_obj_type.isoop = parse_val_into_field(bool_convert, item, 'Составляющий', tmp_dict_obj_type, 'isoop')

        tmp_dict_obj_type.extid = parse_val_into_field(str, item, 'Код', tmp_dict_obj_type, 'extid')

        if not models.DictObjType.objects.filter(code=tmp_dict_obj_type.code,
                                                 numcode=tmp_dict_obj_type.numcode,
                                                 shortname=tmp_dict_obj_type.shortname,
                                                 fullname=tmp_dict_obj_type.fullname,
                                                 abbrname=tmp_dict_obj_type.abbrname,
                                                 constname=tmp_dict_obj_type.constname,
                                                 prefix=tmp_dict_obj_type.prefix,
                                                 # isoop=tmp_dict_obj_type.isoop,
                                                 extid=tmp_dict_obj_type.extid):
            tmp_dict_obj_type.save()


def study_form_to_model(bs_file):
    """
    Процедура, которая парсит данные о форме обучения в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'ФормаОбучения')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_dict_edu_form = models.DictEduForm()

        tmp_dict_edu_form.code = parse_val_into_field(str, item, 'Код', tmp_dict_edu_form, 'code')

        tmp_dict_edu_form.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_edu_form, 'numcode')

        tmp_dict_edu_form.shortname = parse_val_into_field(str, item, 'Сокращение', tmp_dict_edu_form, 'shortname')

        tmp_dict_edu_form.fullname = parse_val_into_field(str, item, 'ФормаОбучения', tmp_dict_edu_form, 'fullname')

        tmp_dict_edu_form.abbrname = parse_val_into_field(str, item, 'Сокращение', tmp_dict_edu_form, 'abbrname')

        tmp_dict_edu_form.constname = parse_val_into_field(str, item, 'Сокращение', tmp_dict_edu_form, 'constname')

        tmp_dict_edu_form.prefix = parse_val_into_field(str, item, 'Префикс', tmp_dict_edu_form, 'prefix')

        tmp_dict_edu_form.extid = parse_val_into_field(str, item, 'Код', tmp_dict_edu_form, 'extid')

        if not models.DictEduForm.objects.filter(code=tmp_dict_edu_form.code,
                                                 numcode=tmp_dict_edu_form.numcode,
                                                 shortname=tmp_dict_edu_form.shortname,
                                                 fullname=tmp_dict_edu_form.fullname,
                                                 abbrname=tmp_dict_edu_form.abbrname,
                                                 constname=tmp_dict_edu_form.constname,
                                                 prefix=tmp_dict_edu_form.prefix,
                                                 extid=tmp_dict_edu_form.extid):
            tmp_dict_edu_form.save()


def action_types_reference_to_model(bs_file):
    """
    Процедура, которая парсит данные о справочнике типов работ в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'СправочникТипаРабот')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_dict_work_type = models.DictWorkType()

        tmp_dict_work_type.code = parse_val_into_field(str, item, 'Код', tmp_dict_work_type, 'code')

        tmp_dict_work_type.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_work_type, 'numcode')

        tmp_dict_work_type.shortname = parse_val_into_field(str, item, 'Название', tmp_dict_work_type, 'shortname')

        tmp_dict_work_type.fullname = parse_val_into_field(str, item, 'Название', tmp_dict_work_type, 'fullname')

        tmp_dict_work_type.abbrname = parse_val_into_field(str, item, 'Название', tmp_dict_work_type, 'abbrname')

        tmp_dict_work_type.constname = parse_val_into_field(str, item, 'Название', tmp_dict_work_type, 'constname')

        tmp_dict_work_type.extid = parse_val_into_field(str, item, 'Код', tmp_dict_work_type, 'extid')

        if not models.DictWorkType.objects.filter(code=tmp_dict_work_type.code,
                                                  numcode=tmp_dict_work_type.numcode,
                                                  shortname=tmp_dict_work_type.shortname,
                                                  fullname=tmp_dict_work_type.fullname,
                                                  abbrname=tmp_dict_work_type.abbrname,
                                                  constname=tmp_dict_work_type.constname,
                                                  extid=tmp_dict_work_type.extid):
            tmp_dict_work_type.save()


def action_variants_reference_to_model(bs_file):
    """
    Процедура, которая парсит данные о справочнике видов работ в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'СправочникВидыРабот')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:

        tmp_dict_work_kind = models.DictWorkKind()

        try:
            tmp_dict_work_kind.worktype = models.DictWorkType.objects.filter(code=item['КодТипРабот']).first()
        except KeyError:
            pass

        tmp_dict_work_kind.code = parse_val_into_field(str, item, 'Код', tmp_dict_work_kind, 'code')

        tmp_dict_work_kind.numcode = parse_val_into_field(int, item, 'Код', tmp_dict_work_kind, 'numcode')

        tmp_dict_work_kind.shortname = parse_val_into_field(str, item, 'Название', tmp_dict_work_kind, 'shortname')

        tmp_dict_work_kind.fullname = parse_val_into_field(str, item, 'Название', tmp_dict_work_kind, 'fullname')

        tmp_dict_work_kind.abbrname = parse_val_into_field(str, item, 'Аббревиатура', tmp_dict_work_kind, 'abbrname')

        tmp_dict_work_kind.constname = parse_val_into_field(str, item, 'Название', tmp_dict_work_kind, 'constname')

        tmp_dict_work_kind.prefix = None

        tmp_dict_work_kind.iscontact = parse_val_into_field(bool_convert, item, 'Контактный', tmp_dict_work_kind,
                                                            'iscontact')

        tmp_dict_work_kind.isclassroom = parse_val_into_field(bool_convert, item, 'Аудиторный', tmp_dict_work_kind,
                                                              'isclassroom')

        tmp_dict_work_kind.hasinter = parse_val_into_field(bool_convert, item, 'HasInter', tmp_dict_work_kind,
                                                           'hasinter')

        tmp_dict_work_kind.hasdistr = parse_val_into_field(bool_convert, item, 'HasDistr', tmp_dict_work_kind,
                                                           'hasdistr')

        tmp_dict_work_kind.haspreparing = parse_val_into_field(bool_convert, item, 'HasPrPreparing', tmp_dict_work_kind,
                                                               'haspreparing')

        tmp_dict_work_kind.extid = parse_val_into_field(str, item, 'msdata:rowOrder', tmp_dict_work_kind, 'extid')

        if not models.DictWorkKind.objects.filter(worktype=tmp_dict_work_kind.worktype,
                                                  code=tmp_dict_work_kind.code,
                                                  numcode=tmp_dict_work_kind.numcode,
                                                  shortname=tmp_dict_work_kind.shortname,
                                                  fullname=tmp_dict_work_kind.fullname,
                                                  abbrname=tmp_dict_work_kind.abbrname,
                                                  constname=tmp_dict_work_kind.constname,
                                                  prefix=tmp_dict_work_kind.prefix,
                                                  iscontact=tmp_dict_work_kind.iscontact,
                                                  isclassroom=tmp_dict_work_kind.isclassroom,
                                                  hasinter=tmp_dict_work_kind.hasinter,
                                                  hasdistr=tmp_dict_work_kind.hasdistr,
                                                  haspreparing=tmp_dict_work_kind.haspreparing,
                                                  extid=tmp_dict_work_kind.extid):
            tmp_dict_work_kind.save()


def other_degree_level_to_model(bs_file):
    """
    Процедура, которая парсит данные о другом уровне образования в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'Уровень_образования')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:

        tmp_dict_edu_qualifi = models.DictEduQualifi()

        tmp_dict_edu_qualifi.edulevelplan = parse_val_into_field(str, item, 'ВидПлана', tmp_dict_edu_qualifi,
                                                                 'edulevelplan')

        try:
            query_res = models.DictEduLvl.objects.filter(constname=item['Категория']).first()

            if query_res:
                tmp_dict_edu_qualifi.edutype = query_res
            else:
                tmp_dict_edu_lvl_c = models.DictEduLvl()

                tmp_dict_edu_lvl_c.shortname = item['Категория']
                tmp_dict_edu_lvl_c.fullname = item['Категория']
                tmp_dict_edu_lvl_c.abbrname = item['Категория']
                tmp_dict_edu_lvl_c.constname = item['Категория']

                tmp_dict_edu_lvl_c.save()
                tmp_dict_edu_qualifi.edutype = tmp_dict_edu_lvl_c

        except ValueError:
            pass

        tmp_dict_edu_qualifi.code = parse_val_into_field(str, item, 'Код_записи', tmp_dict_edu_qualifi, 'code')

        tmp_dict_edu_qualifi.numcode = parse_val_into_field(int, item, 'Код_записи', tmp_dict_edu_qualifi, 'numcode')

        tmp_dict_edu_qualifi.shortname = parse_val_into_field(str, item, 'Примечание', tmp_dict_edu_qualifi,
                                                              'shortname')

        tmp_dict_edu_qualifi.fullname = parse_val_into_field(str, item, 'Уровень', tmp_dict_edu_qualifi, 'fullname')

        tmp_dict_edu_qualifi.prefix = parse_val_into_field(str, item, 'Префикс', tmp_dict_edu_qualifi, 'prefix')

        tmp_dict_edu_qualifi.extid = parse_val_into_field(str, item, 'Шифр', tmp_dict_edu_qualifi, 'extid')

        if not models.DictEduQualifi.objects.filter(edulevelplan=tmp_dict_edu_qualifi.edulevelplan,
                                                    edutype=tmp_dict_edu_qualifi.edutype,
                                                    code=tmp_dict_edu_qualifi.code,
                                                    numcode=tmp_dict_edu_qualifi.numcode,
                                                    shortname=tmp_dict_edu_qualifi.shortname,
                                                    fullname=tmp_dict_edu_qualifi.fullname,
                                                    prefix=tmp_dict_edu_qualifi.prefix,
                                                    extid=tmp_dict_edu_qualifi.extid):
            tmp_dict_edu_qualifi.save()


def oop_to_model(bs_file):
    """
    Процедура, которая парсит данные о ООП в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'ООП')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:

        if not item.find("ООП"):
            continue

        tmp_dict_edu_program = models.EduDirect()

        tmp_dict_edu_program.parent = None

        tmp_dict_edu_program.code = parse_val_into_field(str, item, 'Шифр', tmp_dict_edu_program, 'code')

        tmp_dict_edu_program.directcode = parse_val_into_field(str, item, 'Код', tmp_dict_edu_program, 'directcode')

        tmp_dict_edu_program.shortname = parse_val_into_field(str, item, 'Префикс', tmp_dict_edu_program, 'shortname')

        tmp_dict_edu_program.fullname = parse_val_into_field(str, item, 'Название', tmp_dict_edu_program, 'fullname')

        try:
            tmp_dict_edu_program.edulvl = models.DictEduLvl.objects.filter(code=item['УровеньОбразования']).first()
        except ValueError:
            pass

        try:
            tmp_dict_edu_program.eduqualifi = models.DictEduQualifi.objects.filter(code=item['Квалификация']).first()
        except ValueError:
            pass

        tmp_dict_edu_program.durationyear = parse_val_into_field(int, item, 'СрокЛет', tmp_dict_edu_program,
                                                                 'durationyear')

        tmp_dict_edu_program.durationmonth = parse_val_into_field(int, item, 'СрокОбученияМесяцев',
                                                                  tmp_dict_edu_program, 'durationmonth')

        tmp_dict_edu_program.fgosno = parse_val_into_field(str, item, 'НомерДокумента', tmp_dict_edu_program, 'fgosno')

        try:
            tmp_dict_edu_program.fgosdate = datetime.strptime(item['ДатаДокумента'][:10], '%Y-%m-%d').date()
        except:
            tmp_dict_edu_program.fgosdate = None

        tmp_dict_edu_program.attesttype = parse_val_into_field(str, item, 'ТипГОСа', tmp_dict_edu_program, 'attesttype')

        tmp_dict_edu_program.programprep = parse_val_into_field(int, item, 'ПрограммаПодготовки', tmp_dict_edu_program,
                                                                'programprep')

        tmp_dict_edu_program.extid = parse_val_into_field(str, item, 'diffgr:id', tmp_dict_edu_program, 'extid')

        tmp_dict_edu_program.parentextid = None

        if not models.EduDirect.objects.filter(parent=tmp_dict_edu_program.parent,
                                               code=tmp_dict_edu_program.code,
                                               directcode=tmp_dict_edu_program.directcode,
                                               shortname=tmp_dict_edu_program.shortname,
                                               fullname=tmp_dict_edu_program.fullname,
                                               edulvl=tmp_dict_edu_program.edulvl,
                                               eduqualifi=tmp_dict_edu_program.eduqualifi,
                                               durationyear=tmp_dict_edu_program.durationyear,
                                               durationmonth=tmp_dict_edu_program.durationmonth,
                                               fgosno=tmp_dict_edu_program.fgosno,
                                               fgosdate=tmp_dict_edu_program.fgosdate,
                                               attesttype=tmp_dict_edu_program.attesttype,
                                               programprep=tmp_dict_edu_program.programprep,
                                               extid=tmp_dict_edu_program.extid,
                                               parentextid=tmp_dict_edu_program.parentextid):
            tmp_dict_edu_program.save()
        else:
            tmp_dict_edu_program = models.EduDirect.objects.filter(parent=tmp_dict_edu_program.parent,
                                                                   code=tmp_dict_edu_program.code,
                                                                   directcode=tmp_dict_edu_program.directcode,
                                                                   shortname=tmp_dict_edu_program.shortname,
                                                                   fullname=tmp_dict_edu_program.fullname,
                                                                   edulvl=tmp_dict_edu_program.edulvl,
                                                                   eduqualifi=tmp_dict_edu_program.eduqualifi,
                                                                   durationyear=tmp_dict_edu_program.durationyear,
                                                                   durationmonth=tmp_dict_edu_program.durationmonth,
                                                                   fgosno=tmp_dict_edu_program.fgosno,
                                                                   fgosdate=tmp_dict_edu_program.fgosdate,
                                                                   attesttype=tmp_dict_edu_program.attesttype,
                                                                   programprep=tmp_dict_edu_program.programprep,
                                                                   extid=tmp_dict_edu_program.extid,
                                                                   parentextid=tmp_dict_edu_program.parentextid).first()

        inner_oop = find_branch_from_xml_all(bs_file, 'ООП')
        if not inner_oop:
            return

        for inner_item in inner_oop:
            tmp_inner_dict_edu_program = models.EduDirect()

            tmp_inner_dict_edu_program.parent = tmp_dict_edu_program

            tmp_inner_dict_edu_program.code = parse_val_into_field(str, item, 'Шифр', tmp_inner_dict_edu_program,
                                                                   'code')

            tmp_inner_dict_edu_program.directcode = parse_val_into_field(str, item, 'Код', tmp_inner_dict_edu_program,
                                                                         'directcode')

            tmp_inner_dict_edu_program.shortname = parse_val_into_field(str, item, 'Префикс',
                                                                        tmp_inner_dict_edu_program, 'shortname')

            tmp_inner_dict_edu_program.fullname = parse_val_into_field(str, item, 'Название',
                                                                       tmp_inner_dict_edu_program, 'fullname')

            try:
                tmp_inner_dict_edu_program.edulvl = models.DictEduLvl.objects.filter(
                    code=inner_item['УровеньОбразования']).first()
            except ValueError:
                pass

            try:
                tmp_inner_dict_edu_program.eduqualifi = models.DictEduQualifi.objects.filter(
                    code=inner_item['Квалификация']).first()
            except ValueError:
                pass

            tmp_inner_dict_edu_program.fgosdate = tmp_dict_edu_program.fgosdate

            tmp_inner_dict_edu_program.durationyear = parse_val_into_field(int, item, 'СрокЛет',
                                                                           tmp_inner_dict_edu_program, 'durationyear')

            tmp_inner_dict_edu_program.durationmonth = parse_val_into_field(int, item, 'СрокОбученияМесяцев',
                                                                            tmp_inner_dict_edu_program, 'durationmonth')

            tmp_inner_dict_edu_program.fgosno = parse_val_into_field(str, item, 'НомерДокумента',
                                                                     tmp_inner_dict_edu_program, 'fgosno')

            tmp_inner_dict_edu_program.fgosdate = tmp_inner_dict_edu_program.fgosdate

            tmp_inner_dict_edu_program.attesttype = parse_val_into_field(str, item, 'ТипГОСа',
                                                                         tmp_inner_dict_edu_program, 'attesttype')

            tmp_inner_dict_edu_program.programprep = parse_val_into_field(int, item, 'ПрограммаПодготовки',
                                                                          tmp_inner_dict_edu_program, 'programprep')

            tmp_inner_dict_edu_program.extid = parse_val_into_field(str, item, 'diffgr:id', tmp_inner_dict_edu_program,
                                                                    'extid')

            tmp_inner_dict_edu_program.parentextid = tmp_inner_dict_edu_program.directcode

            if not models.EduDirect.objects.filter(parent=tmp_inner_dict_edu_program.parent,
                                                   code=tmp_inner_dict_edu_program.code,
                                                   directcode=tmp_inner_dict_edu_program.directcode,
                                                   shortname=tmp_inner_dict_edu_program.shortname,
                                                   fullname=tmp_inner_dict_edu_program.fullname,
                                                   edulvl=tmp_inner_dict_edu_program.edulvl,
                                                   eduqualifi=tmp_inner_dict_edu_program.eduqualifi,
                                                   durationyear=tmp_inner_dict_edu_program.durationyear,
                                                   durationmonth=tmp_inner_dict_edu_program.durationmonth,
                                                   fgosno=tmp_inner_dict_edu_program.fgosno,
                                                   fgosdate=tmp_inner_dict_edu_program.fgosdate,
                                                   attesttype=tmp_inner_dict_edu_program.attesttype,
                                                   programprep=tmp_inner_dict_edu_program.programprep,
                                                   extid=tmp_inner_dict_edu_program.extid,
                                                   parentextid=tmp_inner_dict_edu_program.parentextid):
                tmp_inner_dict_edu_program.save()


def edu_program_to_model(bs_file):
    """
    Процедура, которая парсит данные об учебном плане в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'Планы')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:

        tmp_dict_edu_program = models.EduProgram()

        try:
            tmp_dict_edu_program.code = models.EduDirect.objects.filter(directcode=item['КодООП']).first().code
        except ValueError:
            pass

        tmp_dict_edu_program.programcode = parse_val_into_field(str, item, 'КодООП', tmp_dict_edu_program,
                                                                'programcode')

        tmp_dict_edu_program.shortname = parse_val_into_field(str, item, 'Титул', tmp_dict_edu_program, 'shortname')

        tmp_dict_edu_program.fullname = parse_val_into_field(str, item, 'Титул', tmp_dict_edu_program, 'fullname')

        try:
            tmp_dict_edu_program.edulvl = models.DictEduLvl.objects.filter(code=item['КодУровняОбразования']).first()
        except ValueError:
            pass

        try:
            tmp_dict_edu_program.eduqualifi = models.DictEduQualifi.objects.filter(
                code=item['КодУровняОбразования']).first()
        except ValueError:
            pass

        tmp_dict_edu_program.fgosno = parse_val_into_field(str, item, 'НомерФГОС', tmp_dict_edu_program, 'fgosno')

        try:
            tmp_dict_edu_program.fgosdate = datetime.strptime(item['ДатаГОСа'][:10], '%Y-%m-%d').date()
        except ValueError:
            pass

        tmp_dict_edu_program.durationyear = parse_val_into_field(int, item, 'СрокОбучения', tmp_dict_edu_program,
                                                                 'durationyear')

        tmp_dict_edu_program.durationmonth = parse_val_into_field(int, item, 'СрокОбученияМесяцев',
                                                                  tmp_dict_edu_program, 'durationmonth')

        tmp_dict_edu_program.attesttype = parse_val_into_field(str, item, 'ТипГОСа', tmp_dict_edu_program, 'attesttype')

        tmp_dict_edu_program.programprep = parse_val_into_field(int, item, 'КодПрограммы', tmp_dict_edu_program,
                                                                'programprep')

        try:
            tmp_dict_edu_program.parentextid = models.EduDirect.objects.filter(
                directcode=item['КодООП']).first().directcode
        except ValueError:
            pass

        try:
            tmp_dict_edu_program.studydirect = models.EduDirect.objects.filter(directcode=item['КодООП']).first()
        except ValueError:
            pass

        if not models.EduProgram.objects.filter(code=tmp_dict_edu_program.code,
                                                programcode=tmp_dict_edu_program.programcode,
                                                shortname=tmp_dict_edu_program.shortname,
                                                fullname=tmp_dict_edu_program.fullname,
                                                edulvl=tmp_dict_edu_program.edulvl,
                                                eduqualifi=tmp_dict_edu_program.eduqualifi,
                                                fgosno=tmp_dict_edu_program.fgosno,
                                                fgosdate=tmp_dict_edu_program.fgosdate,
                                                durationyear=tmp_dict_edu_program.durationyear,
                                                durationmonth=tmp_dict_edu_program.durationmonth,
                                                attesttype=tmp_dict_edu_program.attesttype,
                                                programprep=tmp_dict_edu_program.programprep,
                                                studydirect=tmp_dict_edu_program.studydirect,
                                                parentextid=tmp_dict_edu_program.parentextid):
            tmp_dict_edu_program.save()


def study_period_to_model(bs_file):
    """
    Процедура, которая парсит данные об учебном годе в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'Планы')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:

        tmp_dict_study_period = models.Studyperiod()

        tmp_dict_study_period.year = parse_val_into_field(int, item, 'ГодНачалаПодготовки', tmp_dict_study_period,
                                                          'year')

        try:
            tmp_dict_study_period.datebeg = datetime.strptime(item['ГодНачалаПодготовки'] + '-09-01', '%Y-%m-%d').date()
        except:
            tmp_dict_study_period.datebeg = None

        try:
            tmp_dict_study_period.dateend = datetime.strptime(str(int(item['ГодНачалаПодготовки']) + 1) + '-08-31',
                                                              '%Y-%m-%d').date()
        except:
            tmp_dict_study_period.dateend = None

        tmp_dict_study_period.name = parse_val_into_field(str, item, 'УчебныйГод', tmp_dict_study_period, 'name')

        if not models.Studyperiod.objects.filter(year=tmp_dict_study_period.year,
                                                 datebeg=tmp_dict_study_period.datebeg,
                                                 dateend=tmp_dict_study_period.dateend,
                                                 name=tmp_dict_study_period.name):
            tmp_dict_study_period.save()


def department_to_model(bs_file):
    """
    Процедура, которая парсит данные о кафедрах в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """
    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'Кафедры')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_department = models.Department()

        tmp_department.code = parse_val_into_field(str, item, 'Код',
                                                   tmp_department, 'code')

        tmp_department.shortname = parse_val_into_field(str, item,
                                                        'Сокращение', tmp_department,
                                                        'shortname')

        tmp_department.fullname = parse_val_into_field(str, item,
                                                       'Название', tmp_department,
                                                       'fullname')

        tmp_department.extid = parse_val_into_field(str, item,
                                                    'Код', tmp_department, 'extid')

        if not models.Department.objects.filter(code=tmp_department.code,
                                                shortname=tmp_department.shortname,
                                                fullname=tmp_department.fullname,
                                                extid=tmp_department.extid):
            tmp_department.save()


def plans_to_model(bs_file, file_instance):
    """
    Процедура, которая парсит данные о планах в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    :param file_instance: запись о файле
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'Планы')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:

        tmp_dict_plan_prog = models.Planprog()

        try:
            tmp_dict_plan_prog.planfile = models.Studyfile.objects.filter(file=file_instance.file).first()
        except:
            pass

        try:
            tmp_dict_plan_prog.period = models.Studyperiod.objects.filter(name=item['УчебныйГод']).first()
        except ValueError:
            pass

        tmp_dict_plan_prog.yearstart = parse_val_into_field(str, item, 'ГодНачалаПодготовки', tmp_dict_plan_prog,
                                                            'yearstart')

        try:
            tmp_dict_plan_prog.eduprog = models.EduProgram.objects.filter(programcode=item['КодООП']).first()
        except ValueError:
            pass

        tmp_dict_plan_prog.title = parse_val_into_field(str, item, 'Титул', tmp_dict_plan_prog, 'title')

        try:
            tmp_dict_plan_prog.eduform = models.DictEduForm.objects.filter(code=item['КодФормыОбучения']).first()
        except ValueError:
            pass

        try:
            tmp_dict_plan_prog.edulevel = models.DictEduLvl.objects.filter(code=item['КодУровняОбразования']).first()
        except ValueError:
            pass

        try:
            tmp_dict_plan_prog.programtype = models.DictProgramLvl.objects.filter(code=item['КодПрограммы']).first()
        except ValueError:
            pass

        try:
            tmp_dict_plan_prog.qualifi = models.DictEduQualifi.objects.filter(code=item['КодУровняОбразования']).first()
        except ValueError:
            pass

        try:
            tmp_dict_plan_prog.department = models.Department.objects.filter(code=item['КодПрофКафедры']).first()
        except ValueError:
            pass

        try:
            tmp_dict_plan_prog.specializ = models.Dicti.objects.filter(code=item['Специализация']).first()
        except ValueError:
            pass

        tmp_dict_plan_prog.isdistant = parse_val_into_field(bool_convert, item, 'Дистанционное', tmp_dict_plan_prog,
                                                            'isdistant')

        tmp_dict_plan_prog.isshort = parse_val_into_field(bool_convert, item, 'Сокращённое', tmp_dict_plan_prog,
                                                          'isshort')

        tmp_dict_plan_prog.isforeign = parse_val_into_field(bool_convert, item, 'ДляИностранных', tmp_dict_plan_prog,
                                                            'isforeign')

        tmp_dict_plan_prog.ismilitary = parse_val_into_field(bool_convert, item, 'Военные', tmp_dict_plan_prog,
                                                             'ismilitary')

        try:
            tmp_dict_plan_prog.militaryspec = models.Dicti.objects.filter(code=item['ВоеннаяСпециальность']).first()
        except ValueError:
            pass

        try:
            tmp_dict_plan_prog.purpose = models.Dicti.objects.filter(code=item['Предназначение']).first()
        except ValueError:
            pass

        tmp_dict_plan_prog.durationyear = parse_val_into_field(int, item, 'СрокОбучения', tmp_dict_plan_prog,
                                                               'durationyear')

        tmp_dict_plan_prog.durationmonth = parse_val_into_field(int, item, 'СрокОбученияМесяцев', tmp_dict_plan_prog,
                                                                'durationmonth')

        tmp_dict_plan_prog.courseamount = parse_val_into_field(int, item, 'ЧислоКурсов', tmp_dict_plan_prog,
                                                               'courseamount')

        tmp_dict_plan_prog.sessionamount = parse_val_into_field(int, item, 'ЧислоСессий', tmp_dict_plan_prog,
                                                                'sessionamount')

        tmp_dict_plan_prog.semesterpercourse = parse_val_into_field(int, item, 'СеместровНаКурсе', tmp_dict_plan_prog,
                                                                    'semesterpercourse')

        tmp_dict_plan_prog.fgosno = parse_val_into_field(str, item, 'НомерФГОС', tmp_dict_plan_prog, 'fgosno')

        try:
            tmp_dict_plan_prog.fgosdate = datetime.strptime(item['ДатаГОСа'][:10], '%Y-%m-%d').date()
        except:
            tmp_dict_plan_prog.fgosdate = None

        tmp_dict_plan_prog.attesttype = parse_val_into_field(str, item, 'ТипГОСа', tmp_dict_plan_prog, 'attesttype')

        tmp_dict_plan_prog.weekzet = parse_val_into_field(float, item, 'ЗЕТвНеделю', tmp_dict_plan_prog, 'weekzet')

        tmp_dict_plan_prog.scale = parse_val_into_field(float, item, 'Точность', tmp_dict_plan_prog, 'scale')

        tmp_dict_plan_prog.isdviga = parse_val_into_field(bool_convert, item, 'ДвИГА', tmp_dict_plan_prog, 'isdviga')

        tmp_dict_plan_prog.isgviga = parse_val_into_field(bool_convert, item, 'ГвИГА', tmp_dict_plan_prog, 'isgviga')

        tmp_dict_plan_prog.individ = parse_val_into_field(int, item, 'Индивидуальный', tmp_dict_plan_prog, 'individ')

        tmp_dict_plan_prog.hourscredit = parse_val_into_field(float, item, 'ЧасовВКредите', tmp_dict_plan_prog,
                                                              'hourscredit')

        tmp_dict_plan_prog.statusonload = parse_val_into_field(float, item, 'СтатусВНагрузке', tmp_dict_plan_prog,
                                                               'statusonload')

        tmp_dict_plan_prog.hoursstudy = parse_val_into_field(float, item, 'ИзученоКонтЧасов', tmp_dict_plan_prog,
                                                             'hoursstudy')

        if not models.Planprog.objects.filter(planfile=tmp_dict_plan_prog.planfile,
                                              period=tmp_dict_plan_prog.period,
                                              yearstart=tmp_dict_plan_prog.yearstart,
                                              eduprog=tmp_dict_plan_prog.eduprog,
                                              title=tmp_dict_plan_prog.title,
                                              eduform=tmp_dict_plan_prog.eduform,
                                              edulevel=tmp_dict_plan_prog.edulevel,
                                              programtype=tmp_dict_plan_prog.programtype,
                                              qualifi=tmp_dict_plan_prog.qualifi,
                                              department=tmp_dict_plan_prog.department,
                                              specializ=tmp_dict_plan_prog.specializ,
                                              isdistant=tmp_dict_plan_prog.isdistant,
                                              isshort=tmp_dict_plan_prog.isshort,
                                              isforeign=tmp_dict_plan_prog.isforeign,
                                              ismilitary=tmp_dict_plan_prog.ismilitary,
                                              militaryspec=tmp_dict_plan_prog.militaryspec,
                                              purpose=tmp_dict_plan_prog.purpose,
                                              durationyear=tmp_dict_plan_prog.durationyear,
                                              durationmonth=tmp_dict_plan_prog.durationmonth,
                                              courseamount=tmp_dict_plan_prog.courseamount,
                                              sessionamount=tmp_dict_plan_prog.sessionamount,
                                              semesterpercourse=tmp_dict_plan_prog.semesterpercourse,
                                              fgosno=tmp_dict_plan_prog.fgosno,
                                              fgosdate=tmp_dict_plan_prog.fgosdate,
                                              attesttype=tmp_dict_plan_prog.attesttype,
                                              weekzet=tmp_dict_plan_prog.weekzet,
                                              scale=tmp_dict_plan_prog.scale,
                                              isdviga=tmp_dict_plan_prog.isdviga,
                                              isgviga=tmp_dict_plan_prog.isgviga,
                                              individ=tmp_dict_plan_prog.individ,
                                              hourscredit=tmp_dict_plan_prog.hourscredit,
                                              statusonload=tmp_dict_plan_prog.statusonload,
                                              hoursstudy=tmp_dict_plan_prog.hoursstudy,
                                              active=tmp_dict_plan_prog.active):
            tmp_dict_plan_prog.save()


def discipline_to_model(bs_file):
    """
    Процедура, которая парсит данные о дисциплинах в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'ПланыСтроки')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:
        tmp_discipline = models.Discipline()

        tmp_discipline.code = parse_val_into_field(str, item, 'ДисциплинаКод', tmp_discipline, 'code')

        tmp_discipline.numcode = parse_val_into_field(int, item, 'Код', tmp_discipline, 'numcode')

        tmp_discipline.fullname = parse_val_into_field(str, item, 'Дисциплина', tmp_discipline, 'fullname')

        tmp_discipline.isphiscult = parse_val_into_field(bool_convert, item, 'ПризнакФизкультуры', tmp_discipline,
                                                         'isphiscult')

        if not models.Discipline.objects.filter(code=tmp_discipline.code,
                                                numcode=tmp_discipline.numcode,
                                                fullname=tmp_discipline.fullname,
                                                isphiscult=tmp_discipline.isphiscult):
            tmp_discipline.save()


def plans_rows_to_model(bs_file, file_instance):
    """
    Процедура, которая парсит данные о планах строках в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    :param file_instance: запись о файле
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'ПланыСтроки')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:

        tmp_plan_row = models.Planrow()

        try:
            tmp_plan_row.plan = models.Planprog.objects.filter(planfile=file_instance).first()
        except ValueError:
            pass

        try:
            tmp_plan_row.discipline = models.Discipline.objects.filter(code=item['ДисциплинаКод']).first()
        except ValueError:
            pass

        tmp_plan_row.disciplinecode = parse_val_into_field(str, item, 'ДисциплинаКод', tmp_plan_row, 'disciplinecode')

        try:
            tmp_plan_row.objtype = models.DictObjType.objects.filter(code=item['ТипОбъекта']).first()
        except ValueError:
            pass

        try:
            tmp_plan_row.parentobjtype = models.Planrow.objects.filter(
                extrowcode=int(item['КодРодителя'])).first().objtype
        except (KeyError, AttributeError):
            pass

        try:
            tmp_plan_row.objkind = models.DictObjKind.objects.filter(code=item['ВидОбъекта']).first()
        except ValueError:
            pass

        tmp_plan_row.isgym = parse_val_into_field(bool_convert, item, 'ПризнакФизкультуры', tmp_plan_row, 'isgym')

        tmp_plan_row.ispractice = parse_val_into_field(bool_convert, item, 'РассредПрактика', tmp_plan_row,
                                                       'ispractice')

        tmp_plan_row.calcnozet = parse_val_into_field(bool_convert, item, 'СчитатьБезЗЕТ', tmp_plan_row, 'calcnozet')

        tmp_plan_row.calcinplan = parse_val_into_field(bool_convert, item, 'СчитатьВПлане', tmp_plan_row, 'calcinplan')

        tmp_plan_row.notcalccontrol = parse_val_into_field(bool_convert, item, 'НеСчитатьКонтроль', tmp_plan_row,
                                                           'notcalccontrol')

        tmp_plan_row.expenseoutdoor = parse_val_into_field(bool_convert, item, 'ЗаСчетПолевых', tmp_plan_row,
                                                           'expenseoutdoor')

        tmp_plan_row.complexcredit = parse_val_into_field(float, item, 'ТрудоемкостьКредитов', tmp_plan_row,
                                                          'complexcredit')

        tmp_plan_row.hourszetin = parse_val_into_field(float, item, 'ЧасовВЗЕТ', tmp_plan_row, 'hourszetin')

        tmp_plan_row.zetfact = parse_val_into_field(float, item, 'ЗЕТфакт', tmp_plan_row, 'zetfact')

        tmp_plan_row.hourszetby = parse_val_into_field(float, item, 'ЧасовПоЗЕТ', tmp_plan_row, 'hourszetby')

        tmp_plan_row.hoursplanby = parse_val_into_field(float, item, 'ЧасовПоПлану', tmp_plan_row, 'hoursplanby')

        tmp_plan_row.hoursstudy = parse_val_into_field(float, item, 'ПодлежитИзучениюЧасов', tmp_plan_row, 'hoursstudy')

        tmp_plan_row.readonly = parse_val_into_field(bool_convert, item, 'ReadOnly', tmp_plan_row, 'readonly')

        tmp_plan_row.unnormalpractice = parse_val_into_field(bool_convert, item, 'НестандартНедПрактики', tmp_plan_row,
                                                             'unnormalpractice')

        tmp_plan_row.score = parse_val_into_field(float, item, 'Оценка', tmp_plan_row, 'score')

        tmp_plan_row.creditclass = parse_val_into_field(int, item, 'ТипПерезачета', tmp_plan_row, 'creditclass')

        tmp_plan_row.adapt = parse_val_into_field(bool_convert, item, 'Адаптационная', tmp_plan_row, 'adapt')

        tmp_plan_row.hoursvarmax = parse_val_into_field(float, item, 'ЧасыВарМакс', tmp_plan_row, 'hoursvarmax')

        tmp_plan_row.hoursvaraudit = parse_val_into_field(float, item, 'ЧасыВарАуд', tmp_plan_row, 'hoursvaraudit')

        tmp_plan_row.hoursauditcredit = parse_val_into_field(float, item, 'ПерезачтеноЧасовАуд', tmp_plan_row,
                                                             'hoursauditcredit')

        tmp_plan_row.notcalcinsumkont = parse_val_into_field(bool_convert, item, 'NotCalcInSumKont', tmp_plan_row,
                                                             'notcalcinsumkont')

        tmp_plan_row.dvnotequals = parse_val_into_field(bool_convert, item, 'DVnotEquals', tmp_plan_row, 'dvnotequals')

        tmp_plan_row.numrow = parse_val_into_field(int, item, 'Номер', tmp_plan_row, 'numrow')

        tmp_plan_row.ordrow = parse_val_into_field(int, item, 'Порядок', tmp_plan_row, 'ordrow')

        tmp_plan_row.extrowcode = parse_val_into_field(int, item, 'Код', tmp_plan_row, 'extrowcode')

        tmp_plan_row.extdepartmentcode = parse_val_into_field(int, item, 'КодКафедры', tmp_plan_row,
                                                              'extdepartmentcode')

        tmp_plan_row.extparentrowcode = parse_val_into_field(int, item, 'КодРодителя', tmp_plan_row, 'extparentrowcode')

        if not models.Planrow.objects.filter(plan=tmp_plan_row.plan,
                                             discipline=tmp_plan_row.discipline,
                                             disciplinecode=tmp_plan_row.disciplinecode,
                                             objtype=tmp_plan_row.objtype,
                                             parentobjtype=tmp_plan_row.parentobjtype,
                                             objkind=tmp_plan_row.objkind,
                                             isgym=tmp_plan_row.isgym,
                                             ispractice=tmp_plan_row.ispractice,
                                             calcnozet=tmp_plan_row.calcnozet,
                                             calcinplan=tmp_plan_row.calcinplan,
                                             notcalccontrol=tmp_plan_row.notcalccontrol,
                                             expenseoutdoor=tmp_plan_row.expenseoutdoor,
                                             complexcredit=tmp_plan_row.complexcredit,
                                             hourszetin=tmp_plan_row.hourszetin,
                                             zetfact=tmp_plan_row.zetfact,
                                             hourszetby=tmp_plan_row.hourszetby,
                                             hoursplanby=tmp_plan_row.hoursplanby,
                                             hoursstudy=tmp_plan_row.hoursstudy,
                                             readonly=tmp_plan_row.readonly,
                                             unnormalpractice=tmp_plan_row.unnormalpractice,
                                             score=tmp_plan_row.score,
                                             creditclass=tmp_plan_row.creditclass,
                                             adapt=tmp_plan_row.adapt,
                                             hoursvarmax=tmp_plan_row.hoursvarmax,
                                             hoursvaraudit=tmp_plan_row.hoursvaraudit,
                                             hoursauditcredit=tmp_plan_row.hoursauditcredit,
                                             notcalcinsumkont=tmp_plan_row.notcalcinsumkont,
                                             dvnotequals=tmp_plan_row.dvnotequals,
                                             numrow=tmp_plan_row.numrow,
                                             ordrow=tmp_plan_row.ordrow,
                                             extrowcode=tmp_plan_row.extrowcode,
                                             extdepartmentcode=tmp_plan_row.extdepartmentcode,
                                             extparentrowcode=tmp_plan_row.extparentrowcode):
            tmp_plan_row.save()


def plans_new_hours_to_model(bs_file, file_instance):
    """
    Процедура, которая парсит данные о планах новых часов в словарь
    :param bs_file: файл для парсинга в формате BeautifulSoup
    :param file_instance: запись о файле
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'ПланыНовыеЧасы')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:

        tmp_plan_hours = models.Planhours()

        try:
            tmp_plan_hours.plan = models.Planprog.objects.filter(planfile=file_instance).first()
        except ValueError:
            pass

        try:
            tmp_plan_hours.discipline = models.Planrow.objects.filter(
                extrowcode=int(item['КодОбъекта'])).first().discipline
        except ValueError:
            pass

        try:
            tmp_plan_hours.parentrow = models.Planrow.objects.filter(extrowcode=int(item['КодОбъекта'])).first().numrow
        except ValueError:
            pass

        try:
            tmp_plan_hours.activitysubclass = models.DictWorkKind.objects.filter(code=item['КодВидаРаботы']).first()
        except ValueError:
            pass

        try:
            tmp_plan_hours.activityclass = models.DictWorkKind.objects.filter(
                code=item['КодВидаРаботы']).first().worktype
        except ValueError:
            pass

        try:
            tmp_plan_hours.hoursclass = models.DictHoursType.objects.filter(code=item['КодТипаЧасов']).first()
        except ValueError:
            pass

        tmp_plan_hours.course = parse_val_into_field(int, item, 'Курс', tmp_plan_hours, 'course')

        tmp_plan_hours.semester = parse_val_into_field(int, item, 'Семестр', tmp_plan_hours, 'semester')

        tmp_plan_hours.session = parse_val_into_field(int, item, 'Сессия', tmp_plan_hours, 'session')

        tmp_plan_hours.weekamount = parse_val_into_field(int, item, 'Недель', tmp_plan_hours, 'weekamount')

        tmp_plan_hours.dayamount = parse_val_into_field(int, item, 'Дней', tmp_plan_hours, 'dayamount')

        tmp_plan_hours.hoursamount = parse_val_into_field(float, item, 'Количество', tmp_plan_hours, 'hoursamount')

        tmp_plan_hours.isreattest = parse_val_into_field(bool_convert, item, 'Переаттестовано', tmp_plan_hours,
                                                         'isreattest')

        tmp_plan_hours.committeeclass = parse_val_into_field(int, item, 'ТипКомиссии', tmp_plan_hours, 'committeeclass')

        tmp_plan_hours.rowcode = parse_val_into_field(int, item, 'msdata:rowOrder', tmp_plan_hours, 'rowcode')

        try:
            tmp_plan_hours.parentrowcode = models.Planrow.objects.filter(
                extrowcode=int(item['КодОбъекта'])).first().parentobjtype.numrow
        except AttributeError:
            pass

        if not models.Planhours.objects.filter(plan=tmp_plan_hours.plan,
                                               discipline=tmp_plan_hours.discipline,
                                               activitysubclass=tmp_plan_hours.activitysubclass,
                                               activityclass=tmp_plan_hours.activityclass,
                                               hoursclass=tmp_plan_hours.hoursclass,
                                               course=tmp_plan_hours.course,
                                               semester=tmp_plan_hours.semester,
                                               session=tmp_plan_hours.session,
                                               weekamount=tmp_plan_hours.weekamount,
                                               dayamount=tmp_plan_hours.dayamount,
                                               hoursamount=tmp_plan_hours.hoursamount,
                                               isreattest=tmp_plan_hours.isreattest,
                                               committeeclass=tmp_plan_hours.committeeclass,
                                               rowcode=tmp_plan_hours.rowcode,
                                               parentrowcode=tmp_plan_hours.parentrowcode):
            tmp_plan_hours.save()


def plans_graphs_cells_to_model(bs_file, file_instance):
    """
    Процедура, которая парсит данные о планах графиках ячейках в БД
    :param bs_file: файл для парсинга в формате BeautifulSoup
    :param file_instance: запись о файле
    """

    # Получаем информацию
    info = find_branch_from_xml_all(bs_file, 'ПланыГрафикиЯчейки')
    if not info:
        return

    # В цикле проходимся по всем пунктам
    for item in info:

        tmp_plan_graf = models.Plangraf()

        try:
            tmp_plan_graf.plan = models.Planprog.objects.filter(planfile=file_instance).first()
        except ValueError:
            pass

        try:
            tmp_plan_graf.activitykind = models.DictWorkKind.objects.filter(extid=item['КодВидаДеятельности']).first()
        except ValueError:
            pass

        tmp_plan_graf.activitykindcode = parse_val_into_field(int, item, 'КодВидаДеятельности', tmp_plan_graf,
                                                              'activitykindcode')

        tmp_plan_graf.weeknum = parse_val_into_field(int, item, 'НомерНедели', tmp_plan_graf, 'weeknum')

        tmp_plan_graf.weekpart = parse_val_into_field(int, item, 'НомерЧастиНедели', tmp_plan_graf, 'weekpart')

        tmp_plan_graf.course = parse_val_into_field(int, item, 'Курс', tmp_plan_graf, 'course')

        tmp_plan_graf.semester = parse_val_into_field(int, item, 'Семестр', tmp_plan_graf, 'semester')

        tmp_plan_graf.isreattest = parse_val_into_field(bool_convert, item, 'Переаттестована', tmp_plan_graf,
                                                        'isreattest')

        tmp_plan_graf.weekpartamount = parse_val_into_field(int, item, 'КоличествоЧастейВНеделе', tmp_plan_graf,
                                                            'weekpartamount')

        tmp_plan_graf.firstweek = parse_val_into_field(int, item, 'НомерПервойНедели', tmp_plan_graf, 'firstweek')

        tmp_plan_graf.IsDist = parse_val_into_field(bool_convert, item, 'IsDist', tmp_plan_graf, 'IsDist')

        tmp_plan_graf.rowcode = parse_val_into_field(int, item, 'msdata:rowOrder', tmp_plan_graf, 'rowcode')

        if not models.Plangraf.objects.filter(plan=tmp_plan_graf.plan,
                                              activitykind=tmp_plan_graf.activitykind,
                                              activitykindcode=tmp_plan_graf.activitykindcode,
                                              weeknum=tmp_plan_graf.weeknum,
                                              weekpart=tmp_plan_graf.weekpart,
                                              course=tmp_plan_graf.course,
                                              semester=tmp_plan_graf.semester,
                                              isreattest=tmp_plan_graf.isreattest,
                                              weekpartamount=tmp_plan_graf.weekpartamount,
                                              firstweek=tmp_plan_graf.firstweek,
                                              IsDist=tmp_plan_graf.IsDist,
                                              rowcode=tmp_plan_graf.rowcode):
            tmp_plan_graf.save()


def parse_file_to_db(instance):
    """
    Функция, которая проводит парсинг данных из файла
    :param instance: запись о файле, который парсится
    """

    # Открываем файл и считываем данные
    with open(instance.file.path, 'r', encoding='utf-16') as file:
        xml_file = file.read()

    # Переводим данные в формат BS4
    soup = BeautifulSoup(xml_file, 'xml')

    study_file_info_to_model(soup, instance, xml_file)
    branches_to_model(soup)
    faculty_to_model(soup)
    degree_level_to_model(soup)
    program_info_to_model(soup)
    reference_base_to_model(soup)
    object_type_to_model(soup)
    practice_type_to_model(soup)
    hours_type_to_model(soup)
    block_type_to_model(soup)
    reference_object_type_to_model(soup)
    study_form_to_model(soup)
    action_types_reference_to_model(soup)
    action_variants_reference_to_model(soup)
    other_degree_level_to_model(soup)
    oop_to_model(soup)
    edu_program_to_model(soup)
    study_period_to_model(soup)
    department_to_model(soup)
    plans_to_model(soup, instance)
    discipline_to_model(soup)
    plans_rows_to_model(soup, instance)
    plans_new_hours_to_model(soup, instance)
    plans_graphs_cells_to_model(soup, instance)

    study_file_additional_to_model(soup, instance)


def change_active_for_models(instance, m_o_i, ref_field):
    """
    Функция, которая обновляет актуальность записей, связанных с данной записью
    :param instance: запись о файле, который обновляется
    :param m_o_i: модель
    :param ref_field: название поля связи модели с объектом
    """

    res = m_o_i.objects.filter(**{str(ref_field): instance})

    for item in res:
        item.active = instance.active
        item.save()


def update_actual_info_for_file(instance):
    """
    Функция, которая обновляет актуальность записей, связанных с файлом
    :param instance: запись о файле, который обновляется
    """

    # Запоминаем текущую актуальность файла
    act = instance.active

    # Учебные планы
    change_active_for_models(instance, models.Planprog, "planfile")


def check_and_update_copy_file(instance):
    """
    Функция, которая проверяет загружен ли новый файл или новая версия файла и изменяет его
    :param instance: запись о файле, который обновляется
    """

    if models.Studyfile.objects.filter(filetext=instance.filetext).count() == 1:
        tmp_dict_plan_prog = models.Planprog.objects.filter(planfile=instance).first()
        tmp_res = models.Planprog.objects.filter(period=tmp_dict_plan_prog.period,
                                                 yearstart=tmp_dict_plan_prog.yearstart,
                                                 eduprog=tmp_dict_plan_prog.eduprog,
                                                 title=tmp_dict_plan_prog.title,
                                                 eduform=tmp_dict_plan_prog.eduform,
                                                 edulevel=tmp_dict_plan_prog.edulevel,
                                                 programtype=tmp_dict_plan_prog.programtype,
                                                 qualifi=tmp_dict_plan_prog.qualifi,
                                                 department=tmp_dict_plan_prog.department,
                                                 specializ=tmp_dict_plan_prog.specializ,
                                                 isdistant=tmp_dict_plan_prog.isdistant,
                                                 isshort=tmp_dict_plan_prog.isshort,
                                                 isforeign=tmp_dict_plan_prog.isforeign,
                                                 ismilitary=tmp_dict_plan_prog.ismilitary,
                                                 militaryspec=tmp_dict_plan_prog.militaryspec,
                                                 purpose=tmp_dict_plan_prog.purpose,
                                                 durationyear=tmp_dict_plan_prog.durationyear,
                                                 durationmonth=tmp_dict_plan_prog.durationmonth,
                                                 courseamount=tmp_dict_plan_prog.courseamount,
                                                 sessionamount=tmp_dict_plan_prog.sessionamount,
                                                 semesterpercourse=tmp_dict_plan_prog.semesterpercourse,
                                                 fgosno=tmp_dict_plan_prog.fgosno,
                                                 fgosdate=tmp_dict_plan_prog.fgosdate,
                                                 attesttype=tmp_dict_plan_prog.attesttype,
                                                 weekzet=tmp_dict_plan_prog.weekzet,
                                                 scale=tmp_dict_plan_prog.scale,
                                                 isdviga=tmp_dict_plan_prog.isdviga,
                                                 isgviga=tmp_dict_plan_prog.isgviga,
                                                 individ=tmp_dict_plan_prog.individ,
                                                 hourscredit=tmp_dict_plan_prog.hourscredit,
                                                 statusonload=tmp_dict_plan_prog.statusonload,
                                                 hoursstudy=tmp_dict_plan_prog.hoursstudy,
                                                 active=True)

        new_res = None
        for item in tmp_res:
            if item != tmp_dict_plan_prog:
                new_res = item.planfile
                break
        if new_res:
            new_res.active = False
            new_res.save()
            update_actual_info_for_file(new_res)
            logger.send_info_to_bot(str(replace_entities("&#8634;")) +
                                    " Обновлен файл учебного расписания '" + new_res.title +
                                    "'. Файл новой версии - '" + instance.title + "'")
            return

    logger.send_info_to_bot(str(replace_entities("&#10010;")) +
                            " Загружен новый файл учебного расписания '" + instance.title + "'")
