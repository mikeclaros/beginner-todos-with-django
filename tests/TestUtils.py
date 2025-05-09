from django.contrib.auth import get_user_model
from django.test import TestCase as DjangoTestCase
from mywebsite.todos.models import List
from mywebsite.todos.forms import EditForm

User = get_user_model()

USER = "tester"
PASS = "pass123"
EMAIL = "a@b.com"


def common_setup(outer):
    outer.User = CommonUtils().create_user_obj()
    outer.client.login(
        username=USER,
        password=PASS,
    )
    outer.user_name = outer.User.username


def login_wrapper(fn):
    def mod_fn(self, *args, **kwargs):
        user = User.objects.create_user(
            username=USER,
            password=PASS,
            email=EMAIL,
            # first_name="fake",
            # last_name="name",
        )
        self.client.login(
            username=USER,
            password=PASS,
        )

        # args = [USER, PASS, EMAIL, user]
        kwargs = {
            "user": USER,
            "pass": PASS,
            "email": EMAIL,
            "user_obj": user,
        }
        return fn(self, *args, **kwargs)

    return mod_fn


class CommonUtils:
    """reusable testing setup"""

    USER = "tester"
    PASS = "pass123"
    EMAIL = "a@b.com"

    def _create_user(self, name, passw, email):
        return User.objects.create_user(
            username=name,
            password=passw,
            email=email,
        )

    def create_user_obj(self):
        """creates default testing user"""
        return User.objects.create_user(
            username=self.USER,
            password=self.PASS,
            email=self.EMAIL,
            # first_name="fake",
            # last_name="name",
        )

    def _login_user(self, client, custom_creds=None):
        username, password = custom_creds if custom_creds else (self.USER, self.PASS)
        client.login(username=username, password=password)

    def login_user(self, client):
        """logs in the default testing user"""
        self._login_user(client)

    def login_diff_user(self, client, custom_creds):
        self._login_user(client, custom_creds)

    def url_helper(self, client, url=None, *args):
        """
        pass in an arg to append to url example: arg=['tester','1']
        where tester is user.username, and 1 is a pk
        """
        if not url:
            url_builder = f"/lists/"
            for arg in list(args):
                url_builder += str(arg) + "/"
            return client.get(url_builder)

        return client.get(url)

    # previous create test user function, some unit tests still use this
    def create_test_user(self):
        """alternative create function with different data. Main create function is create_user_obj"""
        user = User.objects.create_user(
            username="faker",
            password="123fakestreet",
            email="fake@u.com",
        )
        return user

    def create_custom_user(self, username, passw, email):
        return self._create_user(username, passw, email)
