from django.urls import path
from .views import (
    user_lists_view,
    list_todos_view,
    edit_view,
    edit_todo_view,
    delete_view,
    delete_todo_view,
)

app_name = "todos"

urlpatterns = [
    path("<str:username>/", view=user_lists_view, name="lists"),
    path("<str:username>/<int:pk>/", view=list_todos_view, name="todos"),
    path("<str:username>/<int:pk>/edit", view=edit_view, name="edit"),
    path("<str:username>/<int:pk>/delete", view=delete_view, name="delete"),
    path(
        "<str:username>/<int:pk>/<str:todo_id>",
        view=edit_todo_view,
        name="edit-todo",
    ),
    path(
        "<str:username>/<int:pk>/<str:todo_id>/delete-todo",
        view=delete_todo_view,
        name="delete-todo",
    ),
]
