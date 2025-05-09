from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from environment import Constants, browser_connection
from common_functions import wait
from mywebsite.users.models import User
import time


@given("a guest user is created")
def step_impl(context):
    # context.browser.get(context.test.live_server_url)
    browser_connection(context)
    context.browser.find_element(By.ID, "demos").click()
    context.browser.find_element(By.ID, "todo-app").click()
    username = context.browser.find_element(By.ID, "guest-id").text
    context.username = username.replace("Guest: ", "", 1)
    time.sleep(1)


def _click_on_first_list(context):
    div = context.browser.find_element(By.CLASS_NAME, "todo-list-group")
    uls = div.find_elements(By.TAG_NAME, "ul")
    uls[0].find_element(By.TAG_NAME, "a").click()
    time.sleep(1)


def _add_todo_to_list(context, todo="todo 1"):
    # this can be checked for returning to this page
    context.details_url = context.browser.current_url
    context.browser.find_element(By.ID, "btn-toggle").click()
    context.browser.find_element(By.ID, "id_text").send_keys(todo)
    context.browser.find_element(By.ID, "id_text").send_keys(Keys.ENTER)
    time.sleep(1)


def _create_a_list(context):
    context.browser.find_element(By.ID, "todo-app-link").click()
    time.sleep(1)

    list_name = "list 1"
    context.browser.find_element(By.ID, "btn-toggle").click()
    input_box = context.browser.find_element(By.ID, "id_text")
    input_box.send_keys(list_name)
    input_box.send_keys(Keys.ENTER)
    time.sleep(2)
    context.list_name = list_name

    # return to lists page

    context.browser.find_element(By.ID, "todo-app-link").click()


@given("a guest user has a list with todos")
def step_impl(context):
    _create_a_list(context)
    _click_on_first_list(context)
    _add_todo_to_list(context)
    context.browser.find_element(By.ID, "todo-app-link").click()


@given("a guest user has a list")
def step_impl(context):
    _create_a_list(context)


@then("the guest list is deleted")
def step_impl(context):
    div_group = context.browser.find_element(By.CLASS_NAME, "todo-list-group")
    uls = div_group.find_elements(By.TAG_NAME, "ul")
    context.test.assertTrue(len(uls) < 1)


@given("a guest user is on list details page")
def step_impl(context):
    _click_on_first_list(context)


@when("a guest user clicks on a list")
def step_impl(context):
    _click_on_first_list(context)


@then("a guest can see their todos listed")
def step_impl(context):
    div = context.browser.find_element(By.ID, "todo-group")
    uls = div.find_elements(By.TAG_NAME, "ul")
    [context.test.assertTrue(isinstance(ul.text, str)) for ul in uls]


@then("they are sent to details page of list")
def step_impl(context):
    try:
        context.browser.find_element(By.ID, "list-title")
    except WebDriverException as we:
        context.test.fail("element not found!")


@when("a guest user clicks on add new todo")
def step_impl(context):
    context.browser.find_element(By.ID, "btn-toggle").click()


@when("a guest user enters a string")
def step_impl(context):
    context.browser.find_element(By.ID, "id_text").send_keys("this is a str")
    context.browser.find_element(By.ID, "id_text").send_keys(Keys.ENTER)


@then("the todo is created")
def step_impl(context):
    uls = context.browser.find_elements(By.ID, "todo-group")
    context.test.assertTrue(isinstance(uls[0].text, str))


@given("a guest user has a todo in their list")
def step_impl(context):
    _click_on_first_list(context)
    _add_todo_to_list(context)


@when("a guest user enters a duplicate list")
def step_impl(context):
    context.browser.find_element(By.ID, "btn-toggle").click()
    context.browser.find_element(By.ID, "id_text").send_keys("list 1")
    context.browser.find_element(By.ID, "id_text").send_keys(Keys.ENTER)
    time.sleep(1)


@when("a guest user enters a duplicate todo")
def step_impl(context):
    context.browser.find_element(By.ID, "btn-toggle").click()
    context.browser.find_element(By.ID, "id_text").send_keys("todo 1")
    context.browser.find_element(By.ID, "id_text").send_keys(Keys.ENTER)
    time.sleep(1)


@wait
@when("a different guest logs in")
def step_impl(context):
    context.browser.find_element(By.ID, "sign-out").click()
    context.browser.find_element(By.CLASS_NAME, "btn.btn-primary").click()
    context.browser.find_element(By.ID, "demos").click()
    context.browser.find_element(By.ID, "todo-app").click()


@then("they can create a list with the same title")
def step_impl(context):
    try:
        _create_a_list(context)
        elements = context.browser.find_elements(
            By.CLASS_NAME, "alert.alert-block.alert-danger"
        )
        context.test.assertTrue(len(elements) < 1)
    except WebDriverException as we:
        context.test.fail("list unable to create!")


@when("a guest user enters todo with same text as title")
def step_impl(context):
    _add_todo_to_list(context, todo="list 1")


@then("an error message is displayed that todo can't have same text as title")
def step_impl(context):
    div = context.browser.find_element(By.CLASS_NAME, "alert.alert-block.alert-danger")
    actual_error_text = div.find_element(By.TAG_NAME, "li").text
    context.test.assertEqual(actual_error_text, Constants.ErrorMessages.TODO_TITLE_DUPE)


@given("user is found in database")
def step_impl(context):
    user = User.objects.filter(username=context.username)
    context.test.assertTrue(user != None)


@given("the session max age is {4} seconds")
def step_impl(context, expected):
    context.test.assertEqual(context.guest_max_age, expected)


@when("the max age is over")
def step_impl(context):
    time.sleep(int(context.guest_max_age))
    time.sleep(1)


@when("the delete_expired_users task is triggered")
def step_impl(context):
    """simulating a cron job by just running the command"""
    from django.core.management import call_command

    # in cron job it would be ./manage.py delete_expired_users
    call_command("delete_expired_users")


@then("the user should not be in the database")
def step_impl(context):
    result = User.objects.filter(username=context.username)
    context.test.assertTrue(len(result) < 1)
