from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from environment import Constants, SetupUtils, CommonFunctions
from mywebsite.todos.models import List, Todo
import time
import environ


NO_SUCH_ELEMENT_ERROR = "NoSuchElementException Raised!"


def _help_get_email():
    from urllib.parse import urlparse
    import glob

    path = f"{Constants.BASE_DIR}/features/email_data/"
    date = time.strftime("%Y%m%d")
    files = glob.glob1(path, date + "-*-*.log")
    for file in files:
        with open(path + file, "r") as reader:
            for line in reader:
                for word in line.split():
                    result = urlparse(word)
                    if result.scheme and result.netloc:
                        print(result)
                        return result.geturl()


@given("a set of specific users")
def users(context):
    # context.test_user = context.table[0]["name"]
    # context.test_email = context.table[0]["email"]

    # all tests prior to major issues need above variables so
    # the first items will be assigned to those variables
    # and everything after will be assigned to an extra_ array

    context.extra_set_users = []

    def index(row):
        return context.table.rows.index(row)

    # names
    names = []
    rows = context.table.rows
    for row in rows:
        if index(row) == 0:
            context.test_user = row["name"]
            context.test_email = row["email"]
        else:
            context.extra_set_users.append((row["name"], row["email"]))


@given("user is logged in and verified")
def login_user(context):
    """
    Previous scenario should verify user, so user
    verification should not be needed
    """
    setup = SetupUtils()
    setup.login_routine(context)
    setup.verify_email(context)
    setup.login_routine(context)


@given("there is a Todo app link in the header")
def step_impl(context):
    try:
        link = context.browser.find_element(By.ID, "todo-app-link")
        context.link = link
    except NoSuchElementException as e:
        context.test.fail("NoSuchElementException Raised!")


def try_wrapper(fn):
    def mod_fn(context, *args, **kwargs):
        try:
            return fn(context, *args, **kwargs)
        except NoSuchElementException as e:
            context.test.fail(f"{NO_SUCH_ELEMENT_ERROR},\n {e}")

    return mod_fn


@given("user already has some list data")
def step_impl(context):
    SetupUtils().create_list_data(owner=context.user_obj)


@given("a user does not have any lists")
def step_impl(context):
    """check if queryset is empty"""
    if context.user_obj.list_set.all():
        context.test.fail("A list exists!")


@given("they click on the todo app link")
def step_impl(context):
    context.link.click()


@given("they see the page with all their lists")
def step_impl(context):
    text = context.browser.find_element(By.TAG_NAME, "h1").text
    expected = f"{context.test_user}'s Todo Lists"
    context.test.assertEqual(text, expected)
    context.all_lists_url = context.browser.current_url


TODO_ENTRY = "a todo item"


MAX_WAIT = 20


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    return modified_fn


# Scenario: A user wants to check the details page of their todo list
@given("user has a list")
def step_impl(context):
    owner = context.user_obj
    context.first_list_name = "list-1"  # test will only check for first item
    SetupUtils().create_list_data(
        owner=owner, lists=[context.first_list_name, "list-2"]
    )
    SetupUtils().create_todo_data(
        list_=List.objects.first(), todos=["second todo", "todo the third"]
    )
    context.list_length = len(list(List.objects.all()))
    context.test.assertIsNotNone(List.objects.all())


@when(
    "the user navigates to a detail page by clicking on a list from the main lists page"
)
def step_impl(context):
    """clicking on first link"""
    todo_lists = context.browser.find_element(By.CLASS_NAME, "todo-list-group")
    todo_lists.find_elements(By.TAG_NAME, "a")[0].click()


@then("they are redirected to the list's detail page")
def step_impl(context):
    """checking first list"""
    list_name = List.objects.first().name
    expected_title = f"{list_name}"
    actual_title = context.browser.find_element(By.TAG_NAME, "h1").text
    context.test.assertEqual(expected_title, actual_title)


# Scenario: A user can see their todos on the details page
@given("more todos are on the list")
def step_impl(context):
    list_obj = List.objects.first()
    # theres already 3 items in the list; recall first todo is the title
    for x in range(2, 10):
        Todo.objects.create(text=f"a todo {x}", list=list_obj)
    todo_set = list(list_obj.todo_set.all())
    context.todo_set = todo_set
    context.test.assertEqual(len(todo_set), 11)


@then("they can see their todos listed")
def step_impl(context):
    div_group = context.browser.find_element(By.ID, "todo-group")
    todos_list = div_group.find_elements(By.TAG_NAME, "ul")
    todos_list = [x.text for x in todos_list]
    context.test.assertNotEqual(len(todos_list), 0)
    compare = context.todo_set[1:]
    compare = [str(todo) for todo in compare]
    for todos in todos_list:
        context.test.assertIn(todos, compare)


# Scenario: A user wants to add a new todo to a list


@then("an add todo button is displayed")
def step_impl(context):
    button_element = context.browser.find_element(By.ID, "btn-toggle")
    context.test.assertEqual(button_element.text, "Add New Todo")
    context.test.assertIsNotNone(button_element)


@when("they click on the add todo button")
def step_impl(context):
    button_element = context.browser.find_element(By.ID, "btn-toggle")
    button_element.click()
    time.sleep(2)


@then("at the lists detailed page a form is displayed")
def step_impl(context):
    # its not clear why this is returning all the todos in a single string
    # it should just return the first element in the set, which it seems to do on
    # the page itself, for now this is how to get the first element
    user_list_title = context.browser.find_element(By.ID, "list-title").text
    user_list_title = user_list_title.split("\n")[0]
    list_ = List.objects.first()
    actual_title = str(list_.todo_set.first())
    context.test.assertEqual(user_list_title, actual_title)
    form = context.browser.find_element(By.CSS_SELECTOR, ".form-control")
    context.test.assertIsNotNone(form)
    context.form = form


@when("they enter a new entry in the form")
def step_impl(context):
    context.new_todo_str = "new todo check check"
    context.form.send_keys(context.new_todo_str)
    context.form.send_keys(Keys.ENTER)
    time.sleep(2)


@then("a new todo is added to the list")
def step_impl(context):
    todos_element = context.browser.find_elements(By.TAG_NAME, "ul")
    todos = []
    for todo_element in todos_element:
        todos.append(todo_element.text)
    context.test.assertIn(context.new_todo_str, todos)


# Scenario: A user wants to edit a list title


@given("they navigate to their first todo")
def step_impl(context):
    context.lists_url = context.browser.current_url
    div = context.browser.find_element(By.CLASS_NAME, "todo-list-group")
    elements = div.find_elements(By.TAG_NAME, "a")
    title = elements[0].text
    elements[0].click()
    actual_title = context.browser.find_element(By.TAG_NAME, "h1").text
    context.details_url = context.browser.current_url
    context.test.assertEqual(title, actual_title)


@when("they click on the edit link")
def step_impl(context):
    context.browser.find_element(By.ID, "edit").click()
    url = context.browser.current_url
    context.test.assertIn("edit", url)


@then("a form to rename the title of the list is displayed")
def step_impl(context):
    form = context.browser.find_element(By.CSS_SELECTOR, ".form-control")
    context.test.assertIsNotNone(form)


NEW_TITLE = "this is a new title"


@when("they enter a new title and submit")
def step_impl(context):

    # this is needed due to the hidden styling effects on the button
    # this will make the intended form to be interactable
    # without this keyboard is unable to interact because selenium thinks its not interactable
    context.browser.execute_script(
        "document.getElementById('form').style.display='block';"
    )
    # for some reason executing above script causes issues with the forms, and two forms
    # are displayed, this does not happen in the live version but to continue the test
    # the second form is targeted
    element = context.browser.find_elements(By.ID, "edit-form")[1]
    element.send_keys(NEW_TITLE)
    element.send_keys(Keys.ENTER)
    time.sleep(2)


@then("the title is replaced with the new entry")
def step_impl(context):
    text = context.browser.find_element(By.TAG_NAME, "h1").text
    context.test.assertEqual(text, NEW_TITLE)


# Scenario A user wants to edit a todo entry
@then("todos can be selected to be edited")
def step_impl(context):
    div = context.browser.find_element(By.ID, "todos")
    todos = div.find_elements(By.TAG_NAME, "button")
    # if selenium grabbed the button element and its not empty then
    # the it exists as expected
    for todo in todos:
        context.test.assertIsNotNone(todo)


@when("a todo is selected")
def step_impl(context):
    # click on first element
    todos = context.browser.find_element(By.ID, "todos").find_elements(
        By.TAG_NAME, "button"
    )
    try:
        todos[0].click()
    except Exception as e:
        print(f"todo not clickable!\n{e}")

    context.forms = context.browser.find_elements(By.ID, "edit-todo-form")


@then("the edit-todo page displays a form to edit the todo")
def step_impl(context):
    count = 0
    for todo in context.forms:
        context.test.assertIsNotNone(todo)
        count = count + 1
    # only one form should be displayed
    context.test.assertEqual(count, 1)


EDIT_TEXT = "this todo has been edited"


@when("a user submits an edit")
def step_impl(context):
    # get the original text to test if the edit went through
    div = context.browser.find_element(By.ID, "todos")
    # note that getting the ul with the form appeneded, has a label attached
    # so to remove it, the str is split by \n delimiter
    context.original_text = div.find_elements(By.TAG_NAME, "ul")[0].text.split("\n")[0]
    # get input box to enter edit
    entry_box = context.browser.find_elements(By.ID, "edit-todo-form")[0]
    entry_box.send_keys(EDIT_TEXT)
    entry_box.send_keys(Keys.ENTER)
    time.sleep(2)


@then("the edit page updates and shows the new todo")
def step_impl(context):
    div = context.browser.find_element(By.ID, "todo-group")
    new_text = div.find_elements(By.TAG_NAME, "ul")[0].text.split("\n")[0]
    context.test.assertNotEqual(context.original_text, new_text)


@when("they click on the return link")
def step_impl(context):
    context.browser.find_element(By.ID, "return-link").click()
    time.sleep(2)


@then("they are at the todo details page with the recently edited todo")
def step_impl(context):
    expected = context.details_url
    actual = context.browser.current_url
    context.test.assertEqual(expected, actual)


# A user wants to delete a todo list


@when("they click on the delete link")
def step_impl(context):
    link = context.browser.find_element(By.ID, "delete-link")
    context.lists_url = context.browser.current_url
    link.click()
    time.sleep(2)


@then("they are given a confirm prompt")
def step_impl(context):
    prompt = context.browser.find_element(By.ID, "confirm-prompt")
    context.test.assertIsNotNone(prompt)


@when("they click yes")
def step_impl(context):
    context.browser.find_element(By.ID, "yes").click()
    time.sleep(2)


@then("the list is deleted and they are redirected to the lists page")
def step_impl(context):
    # first list was called list-1 after deletion first becomes list-2
    context.test.assertEqual(List.objects.first().name, "list-2")
    context.test.assertEqual(context.all_lists_url, context.browser.current_url)


# A user wants to delete a single todo
@given("there are more than two todos")
def step_impl(context):
    SetupUtils().create_todo_data(
        list_=List.objects.first(), todos=["another todo", "yet another"]
    )
    list_ = list(List.objects.first().todo_set.all())
    context.test.assertGreater(len(list_), 2)


@when("they click on the todo they want to delete")
def step_impl(context):
    # will delete first one
    div = context.browser.find_element(By.ID, "todos")
    # use for later step
    todo = div.find_elements(By.TAG_NAME, "button")[0]
    context.todo_text = todo.text
    todo.click()


@then("they are on the todo edit page")
def step_impl(context):
    try:
        context.browser.find_element(By.ID, "edit-todo-form")
    except Exception as e:
        print(f"Todo edit form not found!\n{e}")


@when("they are on the todo edit page, a delete link is displayed")
def step_impl(context):
    context.delete_link = context.browser.find_element(By.ID, "delete-todo")
    context.test.assertIsNotNone(context.delete_link)


@when("then they click on the delete link")
def step_impl(context):
    context.delete_link.click()


@then("they are redirected to a todo delete page")
def step_impl(context):
    url_param = "delete-todo"
    context.test.assertIn(url_param, context.browser.current_url)


@then("the todo is deleted and they are redirected to the todos list page")
def step_impl(context):
    div = context.browser.find_element(By.ID, "todo-group")
    todos = [todo.text for todo in div.find_elements(By.TAG_NAME, "ul")]
    context.test.assertNotIn(context.todo_text, todos)


# Scenario: A user enters duplicate data, and an error message appears
@when("a user attempts to enter a new list that has the same title as another list")
def step_impl(context):
    # keyboard error bullshit
    context.browser.execute_script(
        "document.getElementById('form').style.display='block';"
    )
    div = context.browser.find_element(By.ID, "form")
    form = div.find_element(By.CSS_SELECTOR, ".form-control")
    form.send_keys(context.first_list_name)
    form.send_keys(Keys.ENTER)
    time.sleep(2)


DUPLICATE_ITEM_ERROR = "This item has already been entered"


@then("an error message appears and the item is not created")
def step_impl(context):

    error_msg = context.browser.find_element(
        By.CSS_SELECTOR, "div.alert.alert-block.alert-danger"
    ).text
    context.test.assertIsNotNone(error_msg)
    context.test.assertEqual(error_msg, DUPLICATE_ITEM_ERROR)


# Scenario: A user enters duplicate todo data, and an error message appears
@when("a user attempts to enter a new todo that has the same title as another todo")
def step_impl(context):

    text = "a todo"
    CommonFunctions().click_and_fill_form(
        Keys=Keys, context=context, text_to_fill_form=text
    )
    # form needs to be refreshed
    context.browser.refresh()
    CommonFunctions().click_and_fill_form(
        Keys=Keys, context=context, text_to_fill_form=text
    )


# Scenario: A user is able to return to list from editing title


@when("they click on the edit icon")
def step_impl(context):
    context.todo_page = context.browser.current_url
    edit_button = context.browser.find_element(By.ID, "edit")
    edit_button.click()
    time.sleep(2)


@when("they are on the edit page")
def step_impl(context):
    url = context.browser.current_url
    context.test.assertIn("edit", url)


@then("there is a return link")
def step_impl(context):
    try:
        link = context.browser.find_element(By.ID, "return-link")
    except NoSuchElementException as we:
        context.test.fail(f"link not found!\n {we}")


@then("they are returned to the todo list")
def step_impl(context):
    time.sleep(2)
    context.test.assertEqual(context.todo_page, context.browser.current_url)


@when('they click on the "{link_text}" link')
def step_impl(context, link_text):
    el = context.browser.find_element(By.ID, "return-link")
    context.test.assertTrue(el.text == link_text)
    el.click()


@then("they are redirected to all lists page")
def step_impl(context):
    username = context.user_obj.username
    title = context.browser.find_element(By.TAG_NAME, "h1").text
    context.test.assertTrue(username in context.browser.current_url)
