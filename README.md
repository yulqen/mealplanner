# Meal Planner

A family meal planning application built with Django, HTMX, and Tailwind CSS.

## Local Development

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- **Tailwind CLI binary**: Download via:
  ```bash
  curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 && chmod +x tailwindcss-linux-x64 && mv tailwindcss-linux-x64 tailwindcss
  ```
  *(Note: Adjust URL for non-Linux platforms)*

### Running the Application

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Database setup**:
   ```bash
   uv run manage.py migrate
   uv run manage.py seed_data
   ```

3. **Start the development server**:
   ```bash
   uv run manage.py runserver
   ```

4. **Watch for CSS changes** (in a separate terminal):
   ```bash
   make css-watch
   ```

### CSS Build Commands

- `make css`: Performs a one-time minified build of `styles.css`.
- `make css-watch`: Watches `input.css` and all templates for changes and rebuilds CSS automatically.
