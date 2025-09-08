"""Routes."""

from django.urls import path

from . import views

app_name = "milalliancetaxes"

urlpatterns = [
    path("", views.redirect_to_current_month, name="redirect_to_current_month"),
    path("view_tax", views.redirect_to_current_month, name="redirect_to_current_month"),
    path("add_character", views.add_character, name="add_character"),
    path("view_tax/<str:year_month>/", views.view_tax, name="view_tax"),
    path("admin_panel", views.admin_panel, name="admin_panel"),
    path("untrack_corporation/<int:corporation_id>", views.untrack_corporation, name="untrack_corporation"),
]
