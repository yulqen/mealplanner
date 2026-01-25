# Specification: Move Shopping List Item

## 1. Overview
This track introduces functionality to transfer a specific ingredient or item from one shopping list to another. Currently, the system supports generating automated lists based on meal plans. This feature enhances flexibility by allowing users to move items between lists (e.g., moving an item from a "Weekly Plan" list to a "General Staples" list) via a modal interface with a selection dropdown.

## 2. Requirements

### Functional Requirements
*   **Move Action**: A user must be able to initiate a "Move" action on any item within a shopping list.
*   **Destination Selection**: The system shall present a modal dialog containing a form to select the destination shopping list.
*   **Input Mechanism**: The selection mechanism shall be a dropdown (`<select>`) populated with available shopping lists belonging to the current user.
*   **Exclusion of Current List**: The dropdown must not list the shopping list where the item currently resides to prevent redundant moves.
*   **Data Transfer**: Upon confirmation, the system must associate the item with the destination shopping list and remove the association with the source shopping list.
*   **Data Integrity**: All existing attributes of the item (quantity, unit, recipe, checked status) must be preserved during the move.
*   **UI Behavior**: The interaction must utilize HTMX to update the UI without a full page reload.

### Non-Functional Requirements
*   **Responsiveness**: The modal must be fully functional on mobile devices, as shopping lists are frequently used in-store on phones.
*   **Latency**: The database update and UI refresh must occur in under 500ms to ensure a smooth user experience.

## 3. Acceptance Criteria
1.  **Scenario**: User views an existing shopping list (List A).
    *   **Given** the user is viewing List A containing at least one item,
    *   **When** the user clicks a "Move" button/icon next to a specific item,
    *   **Then** a modal appears titled "Move Item".
2.  **Scenario**: Selecting a destination.
    *   **Given** the move modal is open,
    *   **When** the user views the destination dropdown,
    *   **Then** they see all shopping lists except List A.
3.  **Scenario**: Successfully moving an item.
    *   **Given** the user has selected a destination list (List B) from the dropdown,
    *   **When** the user confirms the action,
    *   **Then** the item is removed from List A,
    *   **And** the item is added to List B,
    *   **And** the item's quantity and unit remain unchanged,
    *   **And** the modal closes automatically.
4.  **Scenario**: User has no other lists.
    *   **Given** the user has only one shopping list,
    *   **When** the user clicks the "Move" button,
    *   **Then** the system displays a message indicating no other lists are available, or the "Move" button is disabled/hidden.

## 4. Out of Scope
*   **Copying Items**: The ability to copy an item to another list while retaining it in the original list (Duplicating).
*   **List Creation**: The ability to create a brand new shopping list from within the "Move Item" modal (users must create lists via the main list management interface).
*   **Batch Operations**: Moving multiple items simultaneously in a single transaction.
*   **Moving Recipes**: Moving entire recipes or sets of ingredients at once (this spec covers individual ingredients/items only).