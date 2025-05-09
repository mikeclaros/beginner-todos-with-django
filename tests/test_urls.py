from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .TestUtils import CommonUtils
from mywebsite.todos.models import List

User = get_user_model()


class UrlsTest(TestCase):
    def setUp(self) -> None:
        self.User = CommonUtils().create_test_user()
        self.user_name = self.User.username

    def test_user_list_url(self):
        user_name = self.user_name
        expected = f"/lists/{user_name}/"
        actual = reverse("todos:lists", kwargs={"username": f"{user_name}"})
        self.assertEqual(expected, actual)

    def test_user_create_new_list_url(self):
        list_ = List.create_new(text="a todo", owner=self.User)
        expected = f"/lists/{self.user_name}/{list_.pk}/"
        actual = reverse(
            "todos:todos",
            kwargs={"username": f"{self.user_name}", "pk": f"{list_.pk}"},
        )
        self.assertEqual(expected, actual)
