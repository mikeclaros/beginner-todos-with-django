from django.test import TestCase
from mywebsite.todos.models import List, Todo
from mywebsite.todos.forms import (
    TodoForm,
    EditForm,
    EditTodoForm,
    ListForm,
    EMPTY_ITEM_ERROR,
    DUPLICATE_ITEM_ERROR,
)
from unittest.mock import patch
from mywebsite.users.models import User


class FormTestMixin(object):
    form_class = None
    placeholder_text: str = None

    class EditFormTestMixin(object):
        def setUp(self):
            self.form = self.form_class(data={"text": ""})

    def setUp(self):
        self.form = self.form_class(queryset=[], data={"text": ""})

    def test_form_renders_attributes(self):
        as_p = self.form.as_p()
        self.assertIn(f'placeholder="{self.placeholder_text}"', as_p)
        self.assertIn('class="form-control input-lg"', as_p)

    def test_form_validation_for_blank_items(self):
        self.assertFalse(self.form.is_valid())
        self.assertEqual(self.form.errors["text"], [EMPTY_ITEM_ERROR])


class ListFormTest(FormTestMixin, TestCase):
    form_class = ListForm
    placeholder_text = "Enter a title for list. Press enter to submit."

    def test_form_validation_for_duplicate_lists(self):
        user = User.objects.create()
        text = "a list"
        List.create_new(text, owner=user)
        form = self.form_class(queryset=List.objects.all(), data={"text": text})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"], [DUPLICATE_ITEM_ERROR])


class TodoFormTest(FormTestMixin, TestCase):
    form_class = TodoForm
    placeholder_text = "Enter a todo"

    def setUp(self):
        self.list_ = List.objects.create()
        self.form = self.form_class(for_list=self.list_)
        self.form_data = self.form_class(for_list=self.list_, data={"text": ""})

    def test_form_validation_for_duplicate_todos(self):
        list_ = List.objects.create()
        text = "a list name"
        Todo.objects.create(text="unrelated text", list=list_, todo_id="anotherid1")
        Todo.objects.create(text=text, list=list_, todo_id="aunqiueid")
        form = self.form_class(for_list=list_, data={"text": text})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"], [DUPLICATE_ITEM_ERROR])

    def test_form_validation_for_blank_items(self):
        user = User.objects.create()
        text = "list_name"
        list_ = List.create_new(text, owner=user)

        form = self.form_class(for_list=list_, data={"text": ""})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["text"], [EMPTY_ITEM_ERROR])


class EditFormTest(FormTestMixin.EditFormTestMixin, TestCase):
    form_class = EditForm
    placeholder_text = "Enter a new title"

    def test_edit_form_has_id_attr(self):
        self.assertIn('id="edit-form"', self.form.as_p())


class EditTodoFormTest(FormTestMixin.EditFormTestMixin, TestCase):
    form_class = EditTodoForm
    placeholder_text = "Edit Todo entry"

    def test_edit_form_has_id_attr(self):
        form = self.form_class()
        # care with the quotes
        self.assertIn('id="edit-todo-form"', form.as_p())
