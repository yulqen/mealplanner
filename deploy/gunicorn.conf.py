# Gunicorn configuration for Meal Planner
# https://docs.gunicorn.org/en/stable/settings.html


# Bind to localhost only (nginx proxies to us)
bind = "127.0.0.1:8070"

# Workers: 2-4 x CPU cores is typical, but for a small family app, 2 is plenty
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Run as www-data user/group
user = "www-data"
group = "www-data"

# Logging
errorlog = "/var/log/mealplanner/gunicorn-error.log"
accesslog = "/var/log/mealplanner/gunicorn-access.log"
loglevel = "info"
capture_output = True

# Process naming
proc_name = "mealplanner"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
