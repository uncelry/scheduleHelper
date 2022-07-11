from django.urls import path

from . import views


urlpatterns = [
    path("dicti/", views.DictiListView.as_view()),
    # path("dicti/<int:pk>/", views.DictiDetailView.as_view()),
    path("address/", views.AddressListView.as_view()),
    path("address/<int:pk>/", views.AddressDetailView.as_view()),
    path("branch/", views.BranchListView.as_view()),
    path("branch/<int:pk>/", views.BranchDetailView.as_view()),
    path("faculty/", views.FacultyListView.as_view()),
    path("faculty/<int:pk>/", views.FacultyDetailView.as_view()),
    path("department/", views.DepartmentListView.as_view()),
    path("department/<int:pk>/", views.DepartmentDetailView.as_view()),
    path("room/", views.RoomListView.as_view()),
    path("room/<int:pk>/", views.RoomDetailView.as_view()),
    path("subject/", views.SubjectListView.as_view()),
    path("subject/<int:pk>/", views.SubjectDetailView.as_view()),
]