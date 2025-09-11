# Docker Setup for Wagtail Advanced Form Builder

This document explains how to set up and run the Wagtail Advanced Form Builder project using Docker instead of Vagrant.

## Prerequisites

- Docker
- Docker Compose
- Git

## Quick Start

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <your-repo-url>
   cd headless-wagtail-advanced-form
   ```

2. **Build and start the services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Main application: http://localhost:8000
   - Wagtail admin: http://localhost:8000/admin (admin/admin123)
   - MailHog (email testing): http://localhost:8025
   - PostgreSQL: localhost:5432

## Services

The Docker setup includes:

- **web**: Django/Wagtail application (port 8000)
- **db**: PostgreSQL 14 database (port 5432)
- **redis**: Redis cache server (port 6379)
- **mailhog**: Email testing server (SMTP: 1025, Web UI: 8025)

## Development Workflow

### Building and Running

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild specific service
docker-compose build web
```

### Database Management

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access database shell
docker-compose exec db psql -U waf_pg_db -d waf_pg_db
```

### Django Management Commands

```bash
# Run any Django management command
docker-compose exec web python manage.py <command>

# Examples:
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py loaddata <fixture>
```

### Frontend Development

```bash
# Watch for frontend changes (run in separate terminal)
docker-compose exec web npm run watch

# Build production assets
docker-compose exec web npm run build
```

### Logs and Debugging

```bash
# View logs
docker-compose logs web
docker-compose logs db

# Follow logs
docker-compose logs -f web

# Access container shell
docker-compose exec web bash
```

## Environment Variables

Key environment variables (set in `docker-compose.yml`):

- `DJANGO_SETTINGS_MODULE`: Set to `build_test.settings.docker`
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `REDIS_URL`: Redis connection URL
- `EMAIL_HOST`: Email server hostname (MailHog)

## Data Persistence

- PostgreSQL data is persisted in a Docker volume `postgres_data`
- Application code is mounted as a volume for development
- Static files and media are handled within the container

## Differences from Vagrant Setup

| Service | Vagrant | Docker |
|---------|---------|---------|
| Database | PostgreSQL on VM | PostgreSQL container |
| Cache | Memcached | Redis |
| Email | Mailcatcher | MailHog |
| Python | Virtual environment | Container |
| Assets | Built on VM | Built in container |

## Troubleshooting

### Port Conflicts
If you get port conflicts, modify the ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port to 8001
```

### Database Issues
```bash
# Reset database
docker-compose down
docker volume rm headless-wagtail-advanced-form_postgres_data
docker-compose up --build
```

### Permission Issues
```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER .
```

### Fresh Start
```bash
# Complete cleanup and restart
docker-compose down --volumes --rmi local
docker-compose up --build
```

## Production Considerations

For production deployment, consider:
- Use environment-specific settings file
- Set proper secret keys
- Configure proper email backend
- Set up proper static file serving
- Use managed database service
- Implement proper logging
- Set up health checks 