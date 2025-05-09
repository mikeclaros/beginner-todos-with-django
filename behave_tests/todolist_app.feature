Feature: Todo list web app

Background: A user is logged in and verified
    Given a set of specific users
        | name      | email                     |
        | tester    | test123fake@street.com    |
    Given user has a list
    Given user is logged in and verified
        And there is a Todo app link in the header
        And they click on the todo app link
        And they see the page with all their lists
    Given front end does not appear outside of home-page
 

Scenario: A user wants to check the details page of their todo list
    When the user navigates to a detail page by clicking on a list from the main lists page
    Then they are redirected to the list's detail page

Scenario: A user can see their todos on the details page
    Given more todos are on the list
    
    When the user navigates to a detail page by clicking on a list from the main lists page
    Then they can see their todos listed


Scenario: A user wants to add a new todo to a list
    
    When the user navigates to a detail page by clicking on a list from the main lists page
    Then an add todo button is displayed
    When they click on the add todo button
    Then at the lists detailed page a form is displayed
    When they enter a new entry in the form
    Then a new todo is added to the list

Scenario: A user wants to edit a list title
    Given they navigate to their first todo

    When they click on the edit link
    Then a form to rename the title of the list is displayed
    When they enter a new title and submit
    Then the title is replaced with the new entry
    
Scenario: A user wants to edit a todo entry and return to the details page
    Given they navigate to their first todo

    When they click on the edit link
    Then todos can be selected to be edited
    When a todo is selected
    Then the edit-todo page displays a form to edit the todo
    When a user submits an edit
    Then they are at the todo details page with the recently edited todo

Scenario: A user wants to delete a todo list
    Given they navigate to their first todo

    When they click on the delete link
    Then they are given a confirm prompt

    When they click yes
    Then the list is deleted and they are redirected to the lists page
    
Scenario: A user wants to delete a single todo
    Given there are more than two todos
    Given they navigate to their first todo

    When they click on the edit link
        And they click on the todo they want to delete
    Then they are on the todo edit page

    When they are on the todo edit page, a delete link is displayed
        And then they click on the delete link
    Then they are redirected to a todo delete page

    When they click yes
    Then the todo is deleted and they are redirected to the todos list page

Scenario: A user enters duplicate data, and an error message appears
    When a user attempts to enter a new list that has the same title as another list
    Then an error message appears and the item is not created

Scenario: A user enters duplicate todo data, and an error message appears
    Given they navigate to their first todo

    When a user attempts to enter a new todo that has the same title as another todo
    Then an error message appears and the item is not created

Scenario: A user is able to return to list from editing title
    When the user navigates to a detail page by clicking on a list from the main lists page
    When they click on the edit icon
    And they are on the edit page
    Then there is a return link
    When they click on the return link
    Then they are returned to the todo list

Scenario: A user is able to return to all lists page
    Given they navigate to their first todo

    When they click on the "Return to lists" link
    Then they are redirected to all lists page