## Phase 1: Preparation and Test Setup

- [x] Task: Analyze existing codebase for "Clear" functionality
    - [x] Identify the template file containing the "Clear" dropdown menu
    - [x] Identify the Django view and URL pattern handling the clearing actions
- [x] Task: Write failing tests for "Clear Checked" logic
    - [x] Create a test case ensuring that a request to the clear endpoint only removes items with `is_checked=True`
    - [x] Create a test case ensuring that items with `is_checked=False` remain in the database
    - [x] Create a test case to verify the "Clear All" functionality is no longer operational or accessible
- [x] Task: Verify phase completion

## Phase 2: Backend Refinement

- [~] Task: Update the backend view for clearing items
    - [ ] Refactor the view logic to filter items by the active shopping list and `checked` status
    - [ ] Ensure the view handles HTMX requests by returning the appropriate partial template
- [ ] Task: Remove or disable "Clear All" backend logic
    - [ ] Remove any specific logic or separate endpoints dedicated to "Clear All" if they are no longer used
- [ ] Task: Run tests and verify coverage
    - [ ] Confirm all new and existing tests pass
    - [ ] Verify that code coverage for the modified view is ≥80%
- [ ] Task: Verify phase completion

## Phase 3: Frontend Refinement

- [ ] Task: Modify the Shopping List template
    - [ ] Remove the current "Clear" dropdown menu component
    - [ ] Implement a single `<button>` labeled "Clear checked items"
    - [ ] Add HTMX attributes (`hx-post`, `hx-target`, `hx-swap`) to the new button for asynchronous updates
- [ ] Task: Manual Verification of UI/UX
    - [ ] Verify the button is clearly visible and styled appropriately
    - [ ] Confirm that clicking the button removes only checked items without a full page reload
    - [ ] Confirm that the "Clear all items" option is completely removed from the UI
- [ ] Task: Verify phase completion

## Phase 4: Final Polish and Cleanup

- [ ] Task: Clean up unused code
    - [ ] Remove any orphaned CSS, JavaScript, or template fragments related to the old dropdown
- [ ] Task: Run full test suite
    - [ ] Ensure no regressions were introduced in other parts of the shopping list
- [ ] Task: Verify phase completion
