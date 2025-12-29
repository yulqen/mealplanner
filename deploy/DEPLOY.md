# Deploying Meal Planner on Debian

This guide deploys Meal Planner to a Debian VPS with:
- **Nginx** as reverse proxy with SSL
- **Gunicorn** as WSGI server
- **Supervisord** for process management (managed by systemd)
- **Let's Encrypt** for SSL certificates

## Prerequisites

- Debian 12 (Bookworm) or later
- Root or sudo access
- Domain pointing to server IP (mealplanner.matthewlemon.com → your VPS IP)

---

## Step 1: Install System Dependencies

```bash
sudo apt update
sudo apt install -y nginx supervisor git curl python3-certbot-nginx
```

## Step 2: Install uv Package Manager

```bash
# As the user who will own the app (or root, then copy to www-data)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Also install for www-data user
sudo -u www-data bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
```

## Step 3: Create Directory Structure

```bash
# Create app and log directories
sudo mkdir -p /var/www/mealplanner
sudo mkdir -p /var/log/mealplanner
sudo mkdir -p /var/www/certbot

# Set ownership
sudo chown -R www-data:www-data /var/www/mealplanner
sudo chown -R www-data:www-data /var/log/mealplanner
```

## Step 4: Clone the Repository

```bash
cd /var/www/mealplanner
sudo -u www-data git clone https://git.sr.ht/~veibareeri/mealplanner .
```

## Step 5: Configure Environment

```bash
# Copy and edit environment file
sudo -u www-data cp deploy/env.production.example .env

# Generate a secret key
python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))"

# Edit .env with the generated key
sudo -u www-data nano .env
```

Your `.env` should look like:
```
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=mealplanner.matthewlemon.com
```

## Step 6: Install Python Dependencies

```bash
cd /var/www/mealplanner
sudo -u www-data /var/www/.local/bin/uv sync
```

## Step 7: Prepare Django

```bash
cd /var/www/mealplanner

# Collect static files
sudo -u www-data /var/www/.local/bin/uv run python manage.py collectstatic --noinput

# Run database migrations
sudo -u www-data /var/www/.local/bin/uv run python manage.py migrate

# Create a superuser (optional, for admin access)
sudo -u www-data /var/www/.local/bin/uv run python manage.py createsuperuser
```

## Step 8: Configure Supervisor

```bash
# Copy supervisor config
sudo cp /var/www/mealplanner/deploy/mealplanner.supervisor.conf /etc/supervisor/conf.d/mealplanner.conf

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mealplanner

# Check status
sudo supervisorctl status mealplanner
```

## Step 9: Configure Nginx (HTTP first)

Before getting SSL, we need nginx running on HTTP:

```bash
# Create a temporary HTTP-only config
sudo tee /etc/nginx/sites-available/mealplanner << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name mealplanner.matthewlemon.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /static/ {
        alias /var/www/mealplanner/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/mealplanner /etc/nginx/sites-enabled/

# Remove default site if present
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

## Step 10: Get SSL Certificate

```bash
# Run certbot (will modify nginx config automatically)
sudo certbot --nginx -d mealplanner.matthewlemon.com

# When prompted, choose to redirect HTTP to HTTPS
```

After certbot runs, replace with the full config:

```bash
sudo cp /var/www/mealplanner/deploy/mealplanner.nginx.conf /etc/nginx/sites-available/mealplanner
sudo nginx -t
sudo systemctl reload nginx
```

## Step 11: Enable Services on Boot

```bash
# Supervisor is managed by systemd on Debian
sudo systemctl enable supervisor
sudo systemctl enable nginx
```

## Step 12: Verify Deployment

```bash
# Check all services
sudo systemctl status supervisor
sudo supervisorctl status mealplanner
sudo systemctl status nginx

# Check logs if needed
sudo tail -f /var/log/mealplanner/gunicorn-error.log
sudo tail -f /var/log/nginx/mealplanner-error.log
```

Visit https://mealplanner.matthewlemon.com in your browser!

---

## Updating the Application

```bash
cd /var/www/mealplanner

# Pull latest code
sudo -u www-data git pull

# Update dependencies
sudo -u www-data /var/www/.local/bin/uv sync

# Collect static files
sudo -u www-data /var/www/.local/bin/uv run python manage.py collectstatic --noinput

# Run migrations
sudo -u www-data /var/www/.local/bin/uv run python manage.py migrate

# Restart application
sudo supervisorctl restart mealplanner
```

---

## Troubleshooting

### Check if gunicorn is running
```bash
sudo supervisorctl status mealplanner
```

### View application logs
```bash
sudo tail -100 /var/log/mealplanner/gunicorn-error.log
sudo tail -100 /var/log/mealplanner/supervisor-stderr.log
```

### Test gunicorn manually
```bash
cd /var/www/mealplanner
sudo -u www-data /var/www/.local/bin/uv run gunicorn --bind 127.0.0.1:8070 mealplanner.wsgi:application
```

### Check nginx config
```bash
sudo nginx -t
sudo tail -100 /var/log/nginx/mealplanner-error.log
```

### Restart everything
```bash
sudo supervisorctl restart mealplanner
sudo systemctl reload nginx
```

---

## Firewall (if using ufw)

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## SSL Certificate Renewal

Certbot sets up automatic renewal. Test it with:

```bash
sudo certbot renew --dry-run
```
