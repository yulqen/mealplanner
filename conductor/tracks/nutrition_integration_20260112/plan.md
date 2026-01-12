# Track Plan: Nutrition Integration Prototype

## Phase 1: Research and Selection
- [ ] Task: Evaluate OpenFoodFacts UK and Nutrionix for UK data quality and API ease of use
- [ ] Task: Select the primary API and document integration strategy in `tech-stack.md`
- [ ] Task: Conductor - User Manual Verification 'Research and Selection' (Protocol in workflow.md)

## Phase 2: Backend Integration
- [ ] Task: Create `core/services/nutrition.py` and implement basic API client
- [ ] Task: Write tests for `NutritionService` with mocked API responses
- [ ] Task: Update `Ingredient` model in `core/models.py` with `calories` and `last_nutritional_update` fields
- [ ] Task: Create and run migrations
- [ ] Task: Implement a management command to fetch nutritional data for existing ingredients
- [ ] Task: Write tests for the management command
- [ ] Task: Conductor - User Manual Verification 'Backend Integration' (Protocol in workflow.md)

## Phase 3: UI Enhancement
- [ ] Task: Update `core/templates/core/recipe_detail.html` to display caloric summary
- [ ] Task: Implement hover-to-reveal detail for ingredient calories using Tailwind and HTMX
- [ ] Task: Update weekly plan view to show total caloric estimate
- [ ] Task: Write integration tests for new UI elements
- [ ] Task: Conductor - User Manual Verification 'UI Enhancement' (Protocol in workflow.md)
