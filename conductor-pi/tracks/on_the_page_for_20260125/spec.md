# Specification: Shopping List "Clear" Functionality Refinement

## 1. Overview
This track involves simplifying the shopping list interface by replacing the existing "Clear" dropdown menu with a single, dedicated button for removing checked items. The primary goal is to improve safety and prevent accidental data loss by removing the "Clear all items" functionality from the user interface.

## 2. Requirements

### Functional Requirements
*   **UI Modification**: Remove the current "Clear" dropdown component from the shopping list page.
*   **New Action Button**: Implement a single button labeled "Clear checked items" in place of the dropdown.
*   **Feature Removal**: Completely remove the "Clear all items" option from the frontend.
*   **Backend Alignment**: Ensure the backend logic supports the deletion of only checked (completed) items for the active shopping list.
*   **HTMX Integration**: The "Clear checked items" action must trigger an asynchronous update using HTMX to refresh the shopping list without a full page reload, maintaining the app's responsive feel.

### Non-Functional Requirements
*   **Usability**: The "Clear checked items" button should be clearly visible and distinct to prevent confusion.
*   **Safety**: By removing "Clear all," the system reduces the risk of destructive user errors.

## 3. Acceptance Criteria
*   The "Clear" dropdown menu is no longer present on the shopping list page.
*   A button labeled "Clear checked items" is visible on the shopping list page.
*   Clicking "Clear checked items" successfully removes only the items that have been marked as checked/completed.
*   Unchecked items remain on the list after the action is performed.
*   The list updates dynamically via HTMX without a full page refresh.
*   There is no visible method for a user to "Clear all items" (both checked and unchecked) simultaneously.

## 4. Out of Scope
*   Adding a confirmation dialog for clearing checked items (unless deemed necessary for UX, but not requested).
*   Implementing an "Undo" feature for cleared items.
*   Modifying the logic for how items are checked or added to the list.
*   Changes to the "Pantry Staples" exclusion logic.
*   Styling changes unrelated to the replacement of the dropdown with the button.