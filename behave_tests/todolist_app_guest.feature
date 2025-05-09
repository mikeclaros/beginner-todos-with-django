@guest
Feature: Guest User for Todo List web app

Background: A guest user is logged in and verified
    Given a guest user is created
 

Scenario: A guest user can check list details page
    Given a guest user has a list
    When a guest user clicks on a list
    Then they are sent to details page of list

Scenario: A guest user can see their todos on the details page
    Given a guest user has a list with todos
    When a guest user clicks on a list
    Then a guest can see their todos listed


Scenario: A guest user wants to add a new todo to a list
    Given a guest user has a list
    When a guest user clicks on a list
        And a guest user clicks on add new todo
        And a guest user enters a string
    Then the todo is created

Scenario: A guest user wants to edit a list title
    Given a guest user has a list
    Given a guest user is on list details page
    When they click on the edit link
    Then a form to rename the title of the list is displayed
    When they enter a new title and submit
    Then the title is replaced with the new entry
    
Scenario: A guest user wants to edit a todo entry and return to the details page
    Given a guest user has a list
    And a guest user has a todo in their list

    When they click on the edit link
    Then todos can be selected to be edited
    When a todo is selected
    Then the edit-todo page displays a form to edit the todo
    When a user submits an edit
    Then the edit page updates and shows the new todo

    
    Then they are at the todo details page with the recently edited todo

Scenario: A guest user wants to delete a todo list
    Given a guest user has a list
    And a guest user is on list details page

    When they click on the delete link
    Then they are given a confirm prompt

    When they click yes
    Then the guest list is deleted
    
Scenario: A guest user wants to delete a single todo
    Given a guest user has a list
    And a guest user has a todo in their list

    When they click on the edit link
        And they click on the todo they want to delete
    Then they are on the todo edit page

    When they are on the todo edit page, a delete link is displayed
        And then they click on the delete link
    Then they are redirected to a todo delete page

    When they click yes
    Then the todo is deleted and they are redirected to the todos list page

Scenario: A guest user enters duplicate list data, and an error message appears
    Given a guest user has a list
    When a guest user enters a duplicate list
    Then an error message appears and the item is not created

Scenario: A guest user enters duplicate todo data, and an error message appears
    Given a guest user has a list
    And a guest user has a todo in their list

    When a guest user enters a duplicate todo
    Then an error message appears and the item is not created

Scenario: Two different guest users can enter the same title
    had a bug where two different users could not enter the same title if one user already
    had entered that title. Basically, the validation logic was checking against ALL List objects, but should only check against a user's List objects.

    Given a guest user has a list
    When a different guest logs in
    Then they can create a list with the same title

Scenario: unable to add a todo with text that is the same as title
    currently the list title is a todo and thus can't have a todo listed with same text. Make error
    message more helpful

    Given a guest user has a list
    And a guest user has a todo in their list
    When a guest user enters todo with same text as title
    Then an error message is displayed that todo can't have same text as title


Scenario: user is deleted after max age expires

Given user is found in database
Given the session max age is 4 seconds
When the max age is over
And the delete_expired_users task is triggered
Then the user should not be in the database