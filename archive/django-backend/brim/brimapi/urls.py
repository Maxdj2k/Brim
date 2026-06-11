from django.urls import path

from .views import (
    admin_users_view,
    create_user_view,
    login_view,
    logout_view,
    public_search_view,
    reviews_view,
    scan_view,
    search_view,
    signup_view,
)

urlpatterns = [
    path("", public_search_view, name="public-search"),
    path("admin-console/", admin_users_view, name="admin-users"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("search/", search_view, name="search"),
    path("scan/", scan_view, name="scan"),
    path("reviews/", reviews_view, name="reviews"),
    path("signup/", signup_view, name="signup"),
    path("users/", create_user_view, name="create-user"),
]
