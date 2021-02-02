from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    # Look for string in URL and pass through function get entry from views.entry
    path("wiki/<str:title>", views.entry, name="entry"),
    path("search", views.search, name="search"),
    path("create", views.create, name="create"),
    path("wiki/<str:title>/edit", views.edit, name="edit"),
    path("wiki/<str:title>/submit", views.submitEdit, name="submitEdit"),
    path("wiki/", views.randomEntry, name="randomEntry")
]
