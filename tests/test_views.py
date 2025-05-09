from django.test import TestCase as DjangoTestCase
from django.contrib.auth import get_user_model
from django import forms
from .TestUtils import login_wrapper
from mywebsite.todos.models import List, Todo
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from .TestUtils import CommonUtils, common_setup
from mywebsite.todos.forms import EditForm, EditTodoForm, TodoForm
import re

User = get_user_model()


USER = CommonUtils.USER
PASS = CommonUtils.PASS
EMAIL = CommonUtils.EMAIL


def create_and_login_another_user(
    self,
    custom_creds=None,
):
    custom_creds = custom_creds or ("tester_b", "apswd123")
    custom = (custom_creds[0], custom_creds[1], "fake@street.com")
    username, passw, email = custom
    self.user_obj_b = CommonUtils().create_custom_user(username, passw, email)
    CommonUtils().login_diff_user(client=self.client, custom_creds=custom_creds)


class AuthorizationTestsMixin:
    path_param = None

    def test_unauthorized_users_denied_access(self):
        custom_creds = ("tester_b", "apswd123")
        custom = (custom_creds[0], custom_creds[1], "fake@street.com")
        username, passw, email = custom
        CommonUtils().create_custom_user(username, passw, email)
        CommonUtils().login_diff_user(client=self.client, custom_creds=custom_creds)
        pk = (
            self.user_list.pk
            if hasattr(self, "user_list")
            else self._get_user_list().pk
        )
        path = f"/lists/{username}/{pk}/" + str(
            self.path_param if self.path_param != None else ""
        )
        response = self.client.get(path)
        self.assertEqual(response.status_code, 403)

    def _get_user_list(self):
        """assume no original user"""
        a_diff_user = CommonUtils().create_custom_user(
            "somebody", "1once23", "told@me.com"
        )
        return List.create_new(text="sometext", owner=a_diff_user)


class CommonViewTestMixin(object):
    USER = CommonUtils.USER
    PASS = CommonUtils.PASS
    EMAIL = CommonUtils.EMAIL

    template_name = None

    def setUp(self):
        self.User = CommonUtils().create_user_obj()
        CommonUtils().login_user(client=self.client)
        self.user_list = List.create_new(text="list example", owner=self.User)
        self.url = f"/lists/{self.User.username}/{self.user_list.pk}/"
        self.first_todo = Todo.objects.create(
            text="second", list=self.user_list, todo_id="secondid_1"
        )

    def test_correct_template_is_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template_name)

    def create_more_todos(self, list_model, num):
        """provide a list and number of todos to create for list"""
        for x in num:
            Todo.objects.create(text=f"text {x}", list=list_model, todo_id=f"{x}")


class UserListDetailedViewTest(
    CommonViewTestMixin, AuthorizationTestsMixin, DjangoTestCase
):
    template_name = "todos/details.html"

    def test_correct_user(self):
        self.assertEqual(str(self.User), self.USER)

    def test_todos_are_available(self):
        Todo.objects.create(text="a new todo", list=self.user_list)
        # total todos are going to be 3
        # setup makes two defaults (including the title)
        expected_count = 3
        url = self.url
        response = self.client.get(url)
        list_template_obj = response.context["object"]
        count = 0
        for todo in list_template_obj.todo_set.all():
            count = count + 1
        self.assertEqual(expected_count, count)

    def test_error_renders_for_duplicate_entry(self):
        text = "dupe dupe"
        list_ = self.user_list
        Todo.objects.create(text=text, list=list_, todo_id="anid1")
        response = self.client.post(self.url, data={"text": text})
        self.assertIsInstance(response.context["form"], TodoForm)

    def test_data_submitted_is_now_in_context(self):
        text = "new data submitted"
        self.client.post(self.url, data={"text": text})
        response = self.client.get(self.url)
        todos = list(response.context["object"].todo_set.all())
        todos_text = [todo.text for todo in todos]
        self.assertIn(text, todos_text)

    def test_errors_does_not_save_to_db(self):
        """create an invalid occurrence by creating a dupe, and count the Todo objects"""
        text = "dupe dupe"
        list_ = self.user_list
        Todo.objects.create(text=text, list=list_, todo_id="anid1")

        # final count should not change from this value
        intial_count = self.user_list.todo_set.all().count()
        response = self.client.post(self.url, data={"text": text})
        final_count = self.user_list.todo_set.all().count()
        self.assertEqual(intial_count, final_count)

        # if we add 1 more valid object then the final count will be 1 more than initial
        Todo.objects.create(text="very new entry", list=list_, todo_id="aid1")
        final_final_count = self.user_list.todo_set.all().count()
        self.assertEqual(final_final_count, intial_count + 1)


class UserListViewTest(DjangoTestCase):
    USER = CommonUtils.USER
    PASS = CommonUtils.PASS
    EMAIL = CommonUtils.EMAIL

    def setUp(self) -> None:
        self.User = CommonUtils().create_user_obj()
        self.client.login(
            username=self.USER,
            password=self.PASS,
        )
        self.user_name = self.User.username

    def _url_helper(self, user_name: str):
        """to help avoid trailing slash issues..."""
        return self.client.get(f"/lists/{user_name}/")

    def test_empty_list_is_handled(self):
        try:
            self._url_helper(self.User.username)
        except (IndexError, ObjectDoesNotExist) as e:
            self.fail(
                f"{type(e)} raised!\nLikely issue with context data object list in view\nError received:{e}"
            )

    def test_user_list_renders_template(self):
        response = self._url_helper(self.User.username)
        self.assertTemplateUsed(response, "todos/lists.html")


class GenericFormViewTestMixin(object):
    edit_url_trailing_path: str = None
    template_name: str = None
    form_placeholder: str = None
    form_class: forms.models.ModelForm = None

    def setUp(self):
        common_setup(self)
        self.list_ = List.create_new("a list", self.User)
        # self.url = f"/lists/{self.User.username}/{self.list_.pk}/edit"
        self.url = (
            f"/lists/{self.User.username}/{self.list_.pk}/{self.edit_url_trailing_path}"
        )

    def test_edit_view_renders_template(self):
        expected = self.template_name
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, expected)

    def test_context_returns_edit_form(self):
        response = self.client.get(self.url)
        form_obj = response.context["form"]
        self.assertEqual(type(form_obj), self.form_class)
        self.assertIn(self.form_placeholder, response.context["form"].as_p())


class EditFormViewTest(
    GenericFormViewTestMixin, AuthorizationTestsMixin, DjangoTestCase
):
    edit_url_trailing_path = "edit"
    template_name = "todos/edit.html"
    form_placeholder = "Enter a new title"
    form_class = EditForm
    path_param = "edit"


class EditTodoFormViewTest(GenericFormViewTestMixin, DjangoTestCase):
    edit_url_trailing_path = "edit-todo"
    template_name = "todos/edit_todo.html"
    form_placeholder = "Edit Todo entry"
    form_class = EditTodoForm

    def test_authorization_with_todo_id(self):
        create_and_login_another_user(self)
        todo_id = self.list_.todo_set.first().todo_id
        pk = self.list_.pk
        path = f"/lists/{self.user_obj_b}/{pk}/{todo_id}"
        response = self.client.get(path)
        self.assertEqual(response.status_code, 403)


class DeleteViewTest(CommonViewTestMixin, AuthorizationTestsMixin, DjangoTestCase):
    template_name = "todos/delete.html"
    path_param = "delete"

    def setUp(self):
        super().setUp()
        self.url = self.url + "delete"

    def test_post_goes_to_lists_page(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, f"/lists/{self.User.username}/")

    def test_post_deletes_List(self):
        response = self.client.post(self.url)
        self.assertIsNone(List.objects.first())


class DeleteTodoViewTest(CommonViewTestMixin, DjangoTestCase):
    template_name = "todos/delete.html"

    def setUp(self):
        super().setUp()
        self._url_for_delete_todo_view()

    def _url_for_delete_todo_view(self):
        todo = list(self.user_list.todo_set.all())[1]
        todo_id = todo.todo_id
        self.url = (
            f"/lists/{self.User.username}/{self.user_list.pk}/{todo_id}/delete-todo"
        )

    def test_correct_template_is_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template_name)

    def test_post_deletes_todo(self):
        """delete second todo, need to ensure actual target is deleted and not just first()"""
        todo = list(self.user_list.todo_set.all())[1]
        self.client.post(self.url)
        self.assertNotIn(todo, list(self.user_list.todo_set.all()))

    def test_redirects_to_list_page(self):
        """redirects to the list page that contains todos"""
        response = self.client.post(self.url)
        self.assertRedirects(
            response, f"/lists/{self.User.username}/{self.user_list.pk}/"
        )

    def test_authorization_with_todo_id(self):
        create_and_login_another_user(self)
        todo_id = self.user_list.todo_set.first().todo_id
        pk = self.user_list.pk
        path = f"/lists/{self.user_obj_b}/{pk}/{todo_id}"
        response = self.client.get(path)
        self.assertEqual(response.status_code, 403)


class TestEndPoints(DjangoTestCase):
    def test_get_on_list_returns_403(self):
        some_str = "ABBA"
        response = self.client.get(f"/lists/{some_str}/")
        self.assertEqual(403, response.status_code)

    def test_get_on_users_not_logged_in_not_name_pattern_returns_403(self):
        some_str = "ABBA"
        response = self.client.get(f"/lists/{some_str}/")
        self.assertEqual(403, response.status_code)

    def test_check_guest_user_in_database(self):
        some_user = "Guest1234"
        response = self.client.get(f"/users/{some_user}/")
        from mywebsite.users.models import User

        user_exists = User.objects.filter(name=some_user).first()

        actual_user = re.search(
            r"Guest\d{4}", self.client.get(f"/users/guest/").content.decode("utf-8")
        ).group(0)
        actual_user_exists = User.objects.filter(username=actual_user).first()

        self.assertTrue(not user_exists and actual_user_exists)

    def test_check_fake_guest_pattern_returns_403(self):
        some_user = "Guest1234"
        response = self.client.get(f"/users/{some_user}/")
        self.assertEqual(403, response.status_code)
