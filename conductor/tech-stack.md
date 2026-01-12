# Tech Stack: Meal Planner

## Backend
- **Language:** Python 3.12+
- **Framework:** Django 6.0+
- **Task Management:** (To be defined as needed, e.g., Celery or Django-Q for API fetching)

## Frontend
- **Interactivity:** HTMX (for dynamic updates without full page reloads)
- **Styling:** Tailwind CSS (Utility-first approach, stock classes)
- **Templating:** Django Template Language

## Data & External APIs
- **Database:** SQLite (Default for development/simplicity)
- **Nutritional APIs:** UK-centric sources (e.g., Nutrionix, OpenFoodFacts UK, or UK Government Food Data)

## Tooling & Infrastructure
- **Package Manager:** `uv`
- **Server:** Gunicorn
- **Proxy/Web Server:** Nginx
- **Process Supervision:** Supervisor
- **Static Files:** Whitenoise
