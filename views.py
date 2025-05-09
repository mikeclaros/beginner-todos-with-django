from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms.forms import BaseForm
from django.http import HttpRequest, HttpResponse
from django.views.generic import (
    ListView,
    FormView,
    DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy
from .models import List, Todo
from .forms import TodoForm, ListForm, EditForm, EditTodoForm


class BaseFormView(FormView):
    form_class = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.kwargs.get("todo_id", None):
            context["todo_id"] = self.kwargs.get("todo_id")
        return context

    def get_success_url(self) -> str:
        """ListForm redirects user to just created todo list (pk saved on form being valid)"""
        return reverse(
            "todos:todos",
            kwargs={
                "username": self.request.user.username,
                "pk": self.kwargs["pk"],
            },
        )


class UserListFormView(LoginRequiredMixin, ListView, BaseFormView):
    model = List
    template_name = "todos/lists.html"
    form_class = ListForm

    def get_queryset(self) -> QuerySet[Any]:
        return List.objects.filter(owner=self.request.user)

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(queryset=self.get_queryset(), **self.get_form_kwargs())

    def form_valid(self, form: Any) -> HttpResponse:
        list_ = form.save(self.request.user)
        self.kwargs = {"list": list_, "pk": list_.pk}  # save list and pk here
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.object_list = self.get_queryset()
        return super().get_context_data(**kwargs)

    def get_login_url(self) -> str:
        """filter out attempts to log back in for guest accounts"""
        from mywebsite.todos.utils import filter_guest_accounts
        from mywebsite.users.models import User

        username = self.kwargs["username"]
        is_user_in_database = User.objects.filter(username=username)
        is_user_guest_account = filter_guest_accounts(self.kwargs["username"])

        # if self.model.objects.filter(username=self.kwargs["username"]).first():
        if is_user_in_database and is_user_guest_account:
            return "/guest_accounts/login/"
        else:
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied


class UserView(UserListFormView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)


user_lists_view = UserView.as_view()


class TodoFormView(LoginRequiredMixin, BaseFormView):
    form_class = TodoForm

    def get_form(self, form_class: type | None = ...) -> BaseForm:
        """override get_form to pass TodoForm with init values to ProcessFormView"""
        list_ = List.objects.get(id=self.kwargs.get("pk"))
        return self.form_class(for_list=list_, **self.get_form_kwargs())

    def form_valid(self, form: Any) -> HttpResponse:
        """if form valid then runs this"""
        user = self.request.user
        pk = self.kwargs.get("pk")
        form.save(owner=user, pk=pk)
        return super().form_valid(form)


class EditFormView(LoginRequiredMixin, BaseFormView):
    form_class = EditForm

    def form_valid(self, form: Any) -> HttpResponse:
        """rename title"""
        list_ = List.objects.get(id=self.kwargs["pk"])
        todo = list_.todo_set.first()
        todo.text = form.cleaned_data["text"]
        todo.save()
        return super().form_valid(form)


class CustomTodoView(LoginRequiredMixin, DetailView):
    model = List

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.object = List.objects.get(id=self.kwargs.get("pk"))
        return super().get_context_data(**kwargs)


class TodoView(CustomTodoView, UserPassesTestMixin, TodoFormView):
    template_name = "todos/details.html"

    def test_func(self) -> bool | None:
        return self.get_object().owner == self.request.user


list_todos_view = TodoView.as_view()


class EditView(EditFormView, UserPassesTestMixin, CustomTodoView):
    template_name = "todos/edit.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self) -> bool | None:
        return self.get_object().owner == self.request.user


edit_view = EditView.as_view()


class EditTodoFormView(LoginRequiredMixin, UserPassesTestMixin, BaseFormView):
    form_class = EditTodoForm

    def form_valid(self, form: Any) -> HttpResponse:
        # todo = Todo.objects.get(todo_id=)
        id = self.kwargs.get("todo_id")
        if id:
            todo = Todo.objects.get(todo_id=id)
            if todo:
                todo.text = form.cleaned_data["text"]
                todo.save()
        return super().form_valid(form)

    def test_func(self) -> bool | None:
        return self.get_object().owner == self.request.user


class EditTodoView(EditTodoFormView, CustomTodoView):
    template_name = "todos/edit_todo.html"


edit_todo_view = EditTodoView.as_view()


class DeleteListView(UserPassesTestMixin, DeleteView):
    template_name = "todos/delete.html"
    model = List

    def get_success_url(self) -> str:
        return reverse(
            "todos:lists", kwargs={"username": f"{self.request.user.username}"}
        )

    def test_func(self) -> bool | None:
        return self.get_object().owner == self.request.user


delete_view = DeleteListView.as_view()


class DeleteTodoView(UserPassesTestMixin, DeleteView):
    model = Todo
    template_name = "todos/delete.html"

    def get_object(self, queryset=None) -> Model:
        """need to override this to filter by todo_id rather than default pk id"""
        if queryset is None:
            queryset = self.get_queryset()

        todo_id = self.kwargs.get("todo_id")
        queryset = queryset.filter(todo_id=todo_id)

        # shamelessly reusing django code...
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                f"No {queryset.model._meta.verbose_name} model found matching the query"
            )
        return obj

    def get_success_url(self) -> str:
        return reverse(
            "todos:todos",
            kwargs={
                "username": f"{self.request.user.username}",
                "pk": f"{self.kwargs.get('pk')}",
            },
        )

    def test_func(self) -> bool | None:
        return self.get_object().list.owner == self.request.user


delete_todo_view = DeleteTodoView.as_view()
