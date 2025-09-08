# Installation

## 🐳 Docker Installation (Recommended)

The easiest way to get started is with Docker, which includes all dependencies and configurations.

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start

1. **Clone and start the system:**
   ```bash
   git clone https://github.com/octavenz/headless-wagtail-advanced-form-builder.git
   cd headless-wagtail-advanced-form-builder
   docker compose up --build -d
   ```

2. **Access the system:**
   - **Wagtail Admin**: http://localhost:8000/admin (admin/admin123)
   - **API Documentation**: http://localhost:8000/api/docs
   - **API Base**: http://localhost:8000/api/

### What's Included
- ✅ PostgreSQL database
- ✅ Redis for caching
- ✅ MailHog for email testing (http://localhost:8025)
- ✅ All Python dependencies
- ✅ Automatic migrations and superuser creation

---

## 📦 Manual Installation

For custom deployments or development environments.

### 1. Install the Package
```bash
pip install headless-waf-builder
```

### 2. Django Settings

Add to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # Wagtail core
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail',
    # Headless WAF Builder
    'headless_waf_builder',
    # Required dependencies
    'django_recaptcha',  # Optional: for reCAPTCHA support
    'ninja',            # For REST API
    # Your apps
    ...
]
```

### 3. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. URL Configuration
```python
# urls.py
from headless_waf_builder.api.router import api

urlpatterns = [
    path('admin/', include(wagtailadmin_urls)),
    path('api/', api.urls),  # Add API endpoints
]
```

### 5. Required Dependencies
```bash
pip install django>=4.2 wagtail>=6 django-ninja pydantic>=2.0 psycopg2-binary
```

---

## 🚀 Production Deployment

### Environment Variables
```bash
# Required
DJANGO_SETTINGS_MODULE=your_project.settings.production
SECRET_KEY=your-secret-key
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user  
POSTGRES_PASSWORD=your_db_password

# Optional
GOOGLE_RECAPTCHA_PUBLIC_KEY=your_public_key
GOOGLE_RECAPTCHA_PRIVATE_KEY=your_private_key
```

### Docker Production
Use the included `docker-compose.yml` as a base and customize for your infrastructure.

---

## ✅ Verify Installation

1. **Check admin access**: Visit `/admin` and log in
2. **Test API**: Visit `/api/docs` for interactive documentation  
3. **Create a form**: Add a FormPage in Wagtail admin
4. **Test API endpoint**: GET `/api/form_by_path/your-form-path`
        
        
        
