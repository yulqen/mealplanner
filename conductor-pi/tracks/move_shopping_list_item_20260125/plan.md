## Phase 1: Backend Data Structure & Logic

- [x] Task: Write tests for moving a shopping list item model
    - [x] Test moving an item from List A to List B
    - [x] Test verifying quantity, unit, and checked status are preserved
    - [x] Test verifying source list association is removed
- [ ] Task: Implement move logic in Shopping Item model/manager
    - [ ] Create method to update item's list association
    - [ ] Ensure all attributes are preserved during the update
- [ ] Task: Verify phase completion

## Phase 2: Backend View & URL Routing

- [ ] Task: Write tests for the Move Item View
    - [ ] Test GET request returns move modal HTML
    - [ ] Test that dropdown excludes the current list
    - [ ] Test POST request successfully moves item
    - [ ] Test response includes HTMX triggers for UI update
- [ ] Task: Implement View for Move Item
    - [ ] Create view to handle GET (render form) and POST (process move)
    - [ ] Filter available lists in context to exclude current list
    - [ ] Handle edge case where no other lists exist
- [ ] Task: Configure URL routing
    - [ ] Add URL path for the move item endpoint
- [ ] Task: Verify phase completion

## Phase 3: Frontend Modal & Interaction

- [ ] Task: Create Move Item Modal HTML Template
    - [ ] Build modal structure with title "Move Item"
    - [ ] Add form with `<select>` dropdown for destination list
    - [ ] Include "Cancel" and "Confirm" buttons
- [ ] Task: Integrate HTMX triggers
    - [ ] Add "Move" button/icon trigger to the shopping list item row
    - [ ] Configure `hx-get` to load modal content
    - [ ] Configure `hx-post` on the form to submit the move action
    - [ ] Configure `hx-swap` to update the UI without reload and close modal
- [ ] Task: Handle "No Other Lists" state
    - [ ] Implement UI check to hide/disable "Move" button if only one list exists
    - [ ] Or display message in modal if no lists available
- [ ] Task: Verify phase completion

## Phase 4: Refinement & Quality Assurance

- [ ] Task: Run Full Test Suite
    - [ ] Ensure all new and existing tests pass
- [ ] Task: Verify Code Coverage
    - [ ] Run coverage report
    - [ ] Ensure coverage is >80% for new code
- [ ] Task: Manual Verification
    - [ ] Test moving item on desktop browser
    - [ ] Test moving item on mobile device (responsiveness)
    - [ ] Verify data integrity in database after move
- [ ] Task: Final Code Review & Cleanup
    - [ ] Remove debug code
    - [ ] Verify linting and style guidelines
- [ ] Task: Verify phase completion