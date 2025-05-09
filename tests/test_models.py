from mywebsite.todos.models import Todo, List
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from psycopg.errors import UniqueViolation
from django.db.utils import IntegrityError

from mywebsite.todos.tests.TestUtils import login_wrapper
from .TestUtils import CommonUtils

User = get_user_model()


class TodoModelTest(TestCase):
    def test_default_text(self):
        todo_obj = Todo()
        self.assertEqual("", todo_obj.text)

    def test_todo_is_related_to_list(self):
        list_ = List.objects.create()
        fake_list = List.objects.create()

        todo_obj = Todo.objects.create(list=list_)

        self.assertNotEqual(todo_obj.list, fake_list)
        self.assertEqual(todo_obj.list, list_)

    def test_cannot_save_empty_todos_in_lsits(self):

        list_ = List.objects.create()
        todo = Todo(list=list_, text="")

        with self.assertRaises(ValidationError):
            """
            save done instead of create, to specifically test
            that ValidationError is raised at the save step
            """
            todo.save()
            todo.full_clean()

    def test_duplicate_todos_are_invalid(self):
        list_ = List.objects.create()
        text = "todo"
        Todo.objects.create(list=list_, text=text)

        # expecting these errors to occur when attempting to save a dupe
        with self.assertRaises(ValidationError):
            dupe = Todo(list=list_, text=text)
            dupe.full_clean()

    def test_CAN_save_same_todo_on_different_list(self):
        list_one = List.objects.create()
        list_two = List.objects.create()

        todo = Todo.objects.create(list=list_one, text="a todo", todo_id="aid1")
        self.assertNotEqual(todo.list, list_two)
        todo.list = list_two
        todo.save()
        todo.full_clean()

        self.assertEqual(todo.list, list_two)

    def test_todo_list_ordering(self):
        """ordering is based off pk; happens to be order of creation"""
        list_ = List.objects.create()
        todo_one = Todo.objects.create(list=list_, text="ab")
        todo_two = Todo.objects.create(list=list_, text="bc")
        todo_three = Todo.objects.create(list=list_, text="1")

        expected_order = [todo_one, todo_two, todo_three]
        self.assertEqual(list(Todo.objects.all()), expected_order)

    def test_todo_string_representation(self):
        list_ = List.objects.create()
        todo = Todo.objects.create(list=list_, text="item")
        expected = "item"
        self.assertEqual(expected, str(todo))

    def test_todo_can_make_todo_id(self):
        list_ = List.objects.create()
        try:
            todo = Todo.objects.create(
                list=list_, text="test", todo_id="a todo id is a string"
            )
        except Exception as e:
            print(f"unable to create todo!\n{e}")

    @login_wrapper
    def test_todo_can_return_todo_id(self, **kwargs):
        list_ = List.create_new(text="this a todo", owner=kwargs["user_obj"])
        todos = list(list_.todo_set.filter(text="this a todo"))
        todo = todos[0]
        self.assertIsNotNone(todo.todo_id)


class ListModelTest(TestCase):

    @login_wrapper
    def test_create_new_creates_list_and_first_todo_returns_reference_to_list(
        self, **kwargs
    ):
        """
        test that creat_new makes a new list. This function also creates a new todo item
        and associates the new list to the new todo item.
        """
        todo_text = "a todo"
        list_ = List.create_new(text=todo_text, owner=kwargs["user_obj"])
        self.assertEqual(Todo.objects.first().text, todo_text)
        # test that the list was associated with the todo
        self.assertEqual(type(List.objects.first()), type(Todo.objects.first().list))
        self.assertEqual(type(list_), List)

    @login_wrapper
    def test_lists_can_have_owners(self, **kwargs):
        List.objects.create(owner=kwargs["user_obj"])
        self.assertIsNotNone(List.objects.first().owner)

    @login_wrapper
    def test_create_new_optionally_saves_owner(self, **kwargs):
        list_ = List.create_new(text="a todo", owner=kwargs["user_obj"])
        self.assertIsNotNone(list_.owner)

    # this was covered in test_create_new_creates_list_and_first_todo_returns_reference_to_list
    # def test_create_returns_new_list_object(self):
    #     self.fail()

    @login_wrapper
    def test_list_name_is_first_item_text(self, **kwargs):
        test_text = "this is name"
        list_ = List.create_new(text=test_text, owner=kwargs["user_obj"])
        self.assertEqual(list_.name, test_text)

    def test_can_get_lists_for_the_correct_user(self):
        """test ensures that the correct list data is gettable for the right user"""
        self.User = CommonUtils().create_user_obj()
        CommonUtils().login_user(self.client)
        faker = User.objects.create_user(
            username="faker",
            password="123fakestreet",
            email="fake@u.com",
        )
        List.create_new("this should not be", owner=faker)

        expected_list = []
        expected_list.append(List.create_new("this should be", owner=self.User))
        expected_list.append(List.create_new("another list", owner=self.User))

        actual_list = list(self.User.list_set.all())
        self.assertListEqual(expected_list, actual_list)

    @login_wrapper
    def test_create_new_adds_todo_id(self, **kwargs):
        list_ = List.create_new(text="a todo", owner=kwargs["user_obj"])
        todos = list(list_.todo_set.filter(text="a todo"))
        todo = todos[0]
        self.assertIsNotNone(todo.todo_id)

    # not sure yet if i want this functionality (sharing of lists)
    # def test_list_has_shared_with_add(self):
    #     self.fail()
