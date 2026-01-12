# Track Spec: Nutrition Integration Prototype

## Goal
Integrate an external nutritional API to automatically fetch and display caloric data for ingredients within the Meal Planner application, focusing on UK-centric data and a minimalist UX.

## Requirements

### Functional Requirements
- **API Integration:** Connect to a UK-relevant nutritional database (e.g., OpenFoodFacts UK).
- **Automated Fetching:** Implement a mechanism to retrieve nutritional data (initially calories) for ingredients based on their name.
- **Data Persistence:** Store the fetched nutritional data in the database to minimize API calls.
- **UI Display:** Show caloric information in recipe details and weekly plans using progressive disclosure (e.g., tooltips or small indicators).

### Non-Functional Requirements
- **Performance:** API calls should be asynchronous or handled via a background task to avoid blocking the main thread.
- **Data Accuracy:** Prioritize UK-specific results for better relevance to local brands and products.
- **Minimalist UX:** Nutritional data should be unobtrusive and integrate seamlessly into the existing UI.

## Technical Design
- **Service Layer:** Create a `NutritionService` to handle API interactions.
- **Model Update:** Add `calories` and `nutritional_data` fields to the `Ingredient` model.
- **View Integration:** Enhance existing templates using HTMX to fetch/display data where appropriate.

## Success Criteria
- [ ] Successfully fetch caloric data for a test set of ingredients from the external API.
- [ ] Store and retrieve this data from the local database.
- [ ] Display the caloric information in the UI according to the product guidelines.
