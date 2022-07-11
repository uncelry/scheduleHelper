from rest_framework import serializers

from .models import Dicti, Address, Branch, Faculty, Department, Room, Subject


class FilterDictiListSerializer(serializers.ListSerializer):
    """Фильтр справочников, только parents"""
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerialaizer(serializers.Serializer):
    """Вывод рекурсивно children"""
    def to_representation(self, value):
        serializer = self.parent.parent__class__(value, context=self.context)
        return serializer.data


class DictListSerializer(serializers.ModelSerializer):
    """Вывод списка справочников"""
    children = RecursiveSerialaizer(many=True)

    class Meta:
        list_serializer_class = FilterDictiListSerializer
        model = Dicti
        fields = ("fullname", "code", "numcode", "abbrname", "constname", "children")


class AddressListSerializer(serializers.ModelSerializer):
    """Список адресов"""

    class Meta:
        model = Address
        fields = ("shortname",)


class AddressDetailSerializer(serializers.ModelSerializer):
    """Вывод адреса"""

    class Meta:
        model = Address
        fields = "__all__"


class BranchListSerializer(serializers.ModelSerializer):
    """Список филиалов"""

    class Meta:
        model = Branch
        fields = ("fullname",)


class BranchDetailSerializer(serializers.ModelSerializer):
    """Вывод филиала"""
    address = serializers.SlugRelatedField("shortname", read_only=True)

    class Meta:
        model = Branch
        exclude = ("active",)


class FacultyListSerializer(serializers.ModelSerializer):
    """Список факультетов"""

    class Meta:
        model = Faculty
        fields = ("fullname",)


class FacultyDetailSerializer(serializers.ModelSerializer):
    """Вывод факультета"""
    address = serializers.SlugRelatedField("shortname", read_only=True)
    branch = serializers.SlugRelatedField("shortname", read_only=True)

    class Meta:
        model = Faculty
        exclude = ("active",)


class DepartmentListSerializer(serializers.ModelSerializer):
    """Список кафедр"""

    class Meta:
        model = Department
        fields = ("fullname",)


class DepartmentDetailSerializer(serializers.ModelSerializer):
    """Вывод кафедры"""
    faculty = serializers.SlugRelatedField("shortname", read_only=True)

    class Meta:
        model = Department
        exclude = ("active", "extid",)


class RoomListSerializer(serializers.ModelSerializer):
    """Список аудиторий"""
    address = serializers.SlugRelatedField("shortname", read_only=True)
    roomclass = serializers.SlugRelatedField("shortname", read_only=True)

    class Meta:
        model = Room
        fields = ("address", "code", "roomclass",)


class RoomDetailSerializer(serializers.ModelSerializer):
    """Вывод аудитории"""
    address = serializers.SlugRelatedField("shortname", read_only=True)
    roomclass = serializers.SlugRelatedField("shortname", read_only=True)

    class Meta:
        model = Room
        exclude = ("active", "extid",)


class SubjectListSerializer(serializers.ModelSerializer):
    """Список людей"""
    subjclass = serializers.SlugRelatedField("shortname", read_only=True)
    academicdegree = serializers.SlugRelatedField("shortname", read_only=True)

    class Meta:
        model = Subject
        fields = ("fullname",)


class SubjectDetailSerializer(serializers.ModelSerializer):
    """Вывод сведений о человеке"""
    subjclass = serializers.SlugRelatedField("shortname", read_only=True)
    academicdegree = serializers.SlugRelatedField("shortname", read_only=True)

    class Meta:
        model = Subject
        exclude = ("active", )
