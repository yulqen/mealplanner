#!/bin/bash
cd /var/www/mealplanner/
# Force discard changes to styles.css if it exists and conflicts
sudo -u www-data git checkout core/static/core/css/styles.css 2>/dev/null || true
sudo -u www-data git pull
sudo -u www-data make css
sudo -u www-data /var/www/.local/bin/uv run python manage.py migrate
sudo -u www-data /var/www/.local/bin/uv run python manage.py collectstatic --noinput
sudo supervisorctl restart mealplanner

# this is in /usr/local/bin/ on the server and can be run from the local machine. See wekan.
