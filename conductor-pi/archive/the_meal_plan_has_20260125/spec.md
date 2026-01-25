# Specification: Dismissible Meal Plan Update Notification

## Overview

This track adds a dismiss button to the "Meal plan has been updated" notification message, allowing users to acknowledge the notification without taking action to update the shopping list. This improves user experience by giving users control over the notification UI and preventing persistent messages from cluttering the interface when users choose not to sync their shopping list.

## Requirements

### Functional Requirements

1. **Dismiss Button**: Add a visible button (e.g., "Dismiss" or an "×" icon) to the "Meal plan has been updated" notification message.

2. **Button Behavior**: When clicked, the dismiss button must:
   - Remove the notification message from the user's view immediately
   - Not trigger any shopping list update or modification
   - Not affect the underlying meal plan data

3. **HTMX Integration**: The dismiss action should use HTMX to remove the notification element from the DOM without a full page reload, consistent with the application's responsive interface patterns.

4. **Notification State Persistence**: Once dismissed, the notification should not reappear until a new meal plan change occurs.

### Non-Functional Requirements

1. **Responsiveness**: The dismiss action should complete within 200ms to feel instantaneous to the user.

2. **Accessibility**: The dismiss button must be keyboard-accessible and include appropriate ARIA labels for screen readers.

3. **Visual Consistency**: The button styling should match the existing application design patterns and be clearly distinguishable as interactive.

### Assumptions

- The "Meal plan has been updated" notification is currently displayed as an HTML element that can be targeted for removal.
- The notification includes an existing action (likely "Update shopping list") and the dismiss button will be added alongside it.
- The notification state is tracked server-side or can be dismissed client-side without backend persistence requirements.
- HTMX is already configured and available in the templates where this notification appears.

## Acceptance Criteria

1. **AC1**: A dismiss button is visible within the "Meal plan has been updated" notification message.

2. **AC2**: Clicking the dismiss button removes the notification from view without refreshing the page.

3. **AC3**: Dismissing the notification does not modify the shopping list or meal plan data.

4. **AC4**: The dismiss button is accessible via keyboard navigation (Tab + Enter/Space).

5. **AC5**: The notification reappears only when a subsequent meal plan modification occurs after dismissal.

6. **AC6**: The dismiss interaction uses HTMX (no custom JavaScript required beyond HTMX attributes).

## Out of Scope

- Modifying the logic that triggers the "Meal plan has been updated" notification
- Adding user preferences for notification behavior (e.g., auto-dismiss timers)
- Notification history or logging of dismissed notifications
- Changes to the "Update shopping list" functionality
- Email or push notifications related to meal plan updates
- Undo functionality for dismissed notifications