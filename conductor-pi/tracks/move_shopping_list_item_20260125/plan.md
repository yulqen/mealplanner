## Phase 1: Backend Data Structure & Logic

- [x] Task: Write tests for moving a shopping list item model
    - [x] Test moving an item from List A to List B
    - [x] Test verifying quantity, unit, and checked status are preserved
    - [x] Test verifying source list association is removed
- [x] Task: Implement move logic in Shopping Item model/manager
    - [x] Create method to update item's list association
    - [x] Ensure all attributes are preserved during the update
- [x] Task: Verify phase completion

## Phase 2: Backend View & URL Routing

- [x] Task: Write tests for the Move Item View
    - [x] Test GET request returns move modal HTML
    - [x] Test that dropdown excludes the current list
    - [x] Test POST request successfully moves item
    - [x] Test response includes HTMX triggers for UI update
- [x] Task: Implement View for Move Item
    - [x] Create view to handle GET (render form) and POST (process move)
    - [x] Filter available lists in context to exclude current list
    - [x] Handle edge case where no other lists exist
- [x] Task: Configure URL routing
    - [x] Add URL path for the move item endpoint
- [x] Task: Verify phase completion

## Phase 3: Frontend Modal & Interaction

- [x] Task: Create Move Item Modal HTML Template
    - [x] Build modal structure with title "Move Item"
    - [x] Add form with `<select>` dropdown for destination list
    - [x] Include "Cancel" and "Confirm" buttons
- [x] Task: Integrate HTMX triggers
    - [x] Add "Move" button/icon trigger to the shopping list item row
    - [x] Configure `hx-get` to load modal content
    - [x] Configure `hx-post` on the form to submit the move action
    - [x] Configure `hx-swap` to update the UI without reload and close modal
- [x] Task: Handle "No Other Lists" state
    - [x] Implement UI check to hide/disable "Move" button if only one list exists
    - [x] Or display message in modal if no lists available
- [x] Task: Verify phase completion

## Phase 4: Refinement & Quality Assurance

- [x] Task: Run Full Test Suite
    - [x] Ensure all new and existing tests pass
- [x] Task: Verify Code Coverage
    - [x] Run coverage report
    - [x] Ensure coverage is >80% for new code
- [ ] Task: Manual Verification
    - [ ] Test moving item on desktop browser
    - [ ] Test moving item on mobile device (responsiveness)
    - [ ] Verify data integrity in database after move
- [x] Task: Final Code Review & Cleanup
    - [x] Remove debug code
    - [x] Verify linting and style guidelines
- [x] Task: Verify phase completion