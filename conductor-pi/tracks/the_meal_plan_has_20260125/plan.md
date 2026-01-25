# Implementation Plan: Dismissible Meal Plan Update Notification

## Phase 1: Analysis & Setup

- [x] Task: Locate existing notification implementation
    - [x] Find the template containing "Meal plan has been updated" notification
    - [x] Identify the current HTML structure and any existing HTMX patterns
    - [x] Document the notification state tracking mechanism (server-side vs client-side)

- [x] Task: Verify phase completion

## Phase 2: Backend Implementation

- [x] Task: Write tests for dismiss notification endpoint
    - [x] Test that dismiss endpoint returns empty response for HTMX swap
    - [x] Test that dismiss endpoint clears notification state in session
    - [x] Test that dismiss endpoint returns appropriate HTTP status (200)
    - [x] Test that dismiss endpoint does not modify meal plan or shopping list data

- [x] Task: Implement dismiss notification endpoint
    - [x] Create URL route for dismiss action (e.g., `/notifications/dismiss/meal-plan-updated/`)
    - [x] Create view function/class to handle dismiss request
    - [x] Clear notification flag from session/state
    - [x] Return empty response suitable for HTMX swap-delete

- [x] Task: Write tests for notification state persistence
    - [x] Test that dismissed notification does not reappear on page reload
    - [x] Test that notification reappears after new meal plan modification

- [x] Task: Implement notification state persistence logic
    - [x] Update session/state handling to track dismissal
    - [x] Ensure new meal plan changes reset the dismissed state

- [x] Task: Verify phase completion

## Phase 3: Frontend Implementation

- [x] Task: Write tests for dismiss button rendering
    - [x] Test that notification includes dismiss button element
    - [x] Test that dismiss button has correct HTMX attributes
    - [x] Test that dismiss button has appropriate accessibility attributes

- [x] Task: Implement dismiss button in notification template
    - [x] Add dismiss button markup alongside existing "Update shopping list" action
    - [x] Add HTMX attributes for dismiss behavior (hx-delete/hx-post, hx-swap, hx-target)
    - [x] Style button to match application design patterns

- [x] Task: Implement accessibility features
    - [x] Add ARIA label for screen readers (e.g., "Dismiss notification")
    - [x] Ensure keyboard navigation works (focusable, activates on Enter/Space)
    - [x] Add appropriate role attribute if using icon-only button

- [x] Task: Verify phase completion

## Phase 4: Integration Testing

- [ ] Task: Write integration tests for full dismiss workflow
    - [ ] Test end-to-end dismiss flow removes notification from DOM
    - [ ] Test that dismissing notification does not affect shopping list data
    - [ ] Test that dismissing notification does not affect meal plan data
    - [ ] Test notification reappears after subsequent meal plan change

- [ ] Task: Write accessibility tests
    - [ ] Test keyboard-only navigation to dismiss button
    - [ ] Test screen reader announces dismiss button correctly

- [ ] Task: Verify phase completion

## Phase 5: Polish & Verification

- [ ] Task: Review code coverage
    - [ ] Run coverage report
    - [ ] Ensure coverage is ≥80% for new code
    - [ ] Add any missing test cases

- [ ] Task: Manual verification of acceptance criteria
    - [ ] AC1: Verify dismiss button is visible in notification
    - [ ] AC2: Verify clicking dismiss removes notification without page refresh
    - [ ] AC3: Verify dismissing does not modify shopping list or meal plan
    - [ ] AC4: Verify keyboard accessibility (Tab + Enter/Space)
    - [ ] AC5: Verify notification reappears only after new meal plan modification
    - [ ] AC6: Verify implementation uses only HTMX (no custom JavaScript)

- [ ] Task: Final code cleanup and documentation
    - [ ] Remove any debug code
    - [ ] Add code comments where necessary
    - [ ] Update any relevant documentation

- [ ] Task: Verify phase completion
