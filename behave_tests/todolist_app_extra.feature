Feature: extra checks for todo list web app

Scenario: A user wants to have a lot of lists
    Given user has a large amount of lists
    Given a set of specific users
            | name      | email                     |
            | tester    | test123fake@street.com    |
    Given user is logged in and verified
        And there is a Todo app link in the header
        And they click on the todo app link
        And they see the page with all their lists

    Then all list items are listed on the browser
        And footer is present at end