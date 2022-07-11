from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Dicti, Address, Branch, Faculty, Department, Room, Subject
from .serializers import DictListSerializer, AddressListSerializer, AddressDetailSerializer, BranchListSerializer, BranchDetailSerializer, \
    FacultyListSerializer, FacultyDetailSerializer, DepartmentListSerializer, DepartmentDetailSerializer, \
    RoomListSerializer, RoomDetailSerializer, SubjectListSerializer, SubjectDetailSerializer


class DictiListView(APIView):
    """Вывод списка справочников"""
    def get(self, request):
        dictions = Dicti.objects.all()
        serializer = DictListSerializer(dictions, many=True)
        return Response(serializer.data)


class AddressListView(APIView):
    """Вывод списка адресов"""
    def get(self, request):
        addresses = Address.objects.all()
        serializer = AddressListSerializer(addresses, many=True)
        return Response(serializer.data)


class AddressDetailView(APIView):
    """Вывод адреса"""
    def get(self, request, pk):
        address = Address.objects.get(id=pk)
        serializer = AddressDetailSerializer(address)
        return Response(serializer.data)


class BranchListView(APIView):
    """Вывод списка филиалов"""
    def get(self, request):
        branches = Branch.objects.filter(active=True)
        serializer = BranchListSerializer(branches, many=True)
        return Response(serializer.data)


class BranchDetailView(APIView):
    """Вывод филиала"""
    def get(self, request, pk):
        branch = Branch.objects.get(id=pk, active=True)
        serializer = BranchDetailSerializer(branch)
        return Response(serializer.data)


class FacultyListView(APIView):
    """Вывод списка факультетов"""
    def get(self, request):
        faculties = Faculty.objects.filter(active=True)
        serializer = FacultyListSerializer(faculties, many=True)
        return Response(serializer.data)


class FacultyDetailView(APIView):
    """Вывод факультета"""
    def get(self, request, pk):
        faculty = Faculty.objects.get(id=pk, active=True)
        serializer = FacultyDetailSerializer(faculty)
        return Response(serializer.data)


class DepartmentListView(APIView):
    """Вывод списка факультетов"""
    def get(self, request):
        departments = Department.objects.filter(active=True)
        serializer = DepartmentListSerializer(departments, many=True)
        return Response(serializer.data)


class DepartmentDetailView(APIView):
    """Вывод факультета"""
    def get(self, request, pk):
        department = Department.objects.get(id=pk, active=True)
        serializer = DepartmentDetailSerializer(department)
        return Response(serializer.data)


class RoomListView(APIView):
    """Вывод списка аудиторий"""
    def get(self, request):
        rooms = Room.objects.filter(active=True)
        serializer = RoomListSerializer(rooms, many=True)
        return Response(serializer.data)


class RoomDetailView(APIView):
    """Вывод аудитории"""
    def get(self, request, pk):
        room = Room.objects.get(id=pk, active=True)
        serializer = RoomDetailSerializer(room)
        return Response(serializer.data)


class SubjectListView(APIView):
    """Вывод списка людей"""
    def get(self, request):
        subjects = Subject.objects.filter(active=True)
        serializer = SubjectListSerializer(subjects, many=True)
        return Response(serializer.data)


class SubjectDetailView(APIView):
    """Вывод сведений о человеке"""
    def get(self, request, pk):
        subject = Subject.objects.get(id=pk, active=True)
        serializer = SubjectDetailSerializer(subject)
        return Response(serializer.data)
