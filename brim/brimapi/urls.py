from django.urls import path

from .views import admin_users_view, create_user_view

urlpatterns = [
    path("", admin_users_view, name="admin-users"),
    path("users/", create_user_view, name="create-user"),
]
