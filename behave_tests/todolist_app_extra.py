from behave import given, when, then
from selenium.webdriver.common.by import By
from environment import Constants, SetupUtils
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time

# Scenario: A user wants to have a lot of lists


@given("user has a large amount of lists")
def step_impl(context):
    list_ = []
    for x in range(0, 1000):
        list_.append(f"king{x}")
    SetupUtils().create_list_data(owner=context.user_obj, lists=list_)
    context.list_to_check = list_


@then("all list items are listed on the browser")
def step_impl(context):
    group_container = context.browser.find_element(By.CLASS_NAME, "todo-list-group")
    todo_list_group_link_text = [
        item.text for item in group_container.find_elements(By.TAG_NAME, "a")
    ]
    for item in context.list_to_check:
        context.test.assertIn(item, todo_list_group_link_text)


@then("footer is present at end")
def step_impl(context):
    context.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    context.test.assertIsNotNone(context.browser.find_element(By.ID, "footer-content"))
