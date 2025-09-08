# Headless Wagtail Advanced Form Builder

![Form fields API](./docs/screenshots/headless_waf_builder_api.png)
![Form fields CMS](./docs/screenshots/headless_waf_builder_cms.png)

**A powerful headless-first Wagtail Advanced Form Builder with complete REST API for modern frontend frameworks like React, Vue, Angular, and mobile applications.**

> **🚨 Important**: This is a separate package from the original `wagtail-advanced-form-builder`. Choose `headless-wagtail-advanced-form-builder` for modern headless/API-first applications, or the original for traditional Wagtail template only usage.

## 🚀 Headless API Features

**Complete REST API with Django Ninja** - Build modern frontend applications with React, Vue, Angular, or any JavaScript framework using our comprehensive headless API.

### API Capabilities
- **📋 Form Retrieval API** - Get form schemas with complete field definitions and validation rules
- **📤 Form Submission API** - Submit forms with automatic validation and processing
- **🔒 Security Built-in** - CSRF protection, reCAPTCHA v2/v3 integration, and rate limiting
- **📧 Email Integration** - Automatic email sending with Celery background processing
- **📖 Auto-Generated Documentation** - Interactive API docs at `/docs` endpoint
- **🎯 Type-Safe Schemas** - Complete Pydantic schemas for all form fields and responses

### Quick API Example
```javascript
// Get form schema
const response = await fetch('/api/form_by_path/contact-form/');
const formSchema = await response.json();

// Submit form data
await fetch('/api/form_by_path/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    path: 'contact-form',
    form_fields: { name: 'John', email: 'john@example.com' },
    recaptcha_token: recaptchaToken // optional
  })
});
```

---

# Versions

This package currently only supports Wagtail 6.4 above.

### Version 1.0.0

**Brand new headless API capabilities** for use with Wagtail version 6.4.X
- **🎯 Complete Headless API** with Django Ninja for modern frontend frameworks
- **📝 Full Schema Models** for all form fields and pages with Pydantic validation
- **🔌 RESTful APIs** for form retrieval, submission, and validation
- **🔒 Security Features** including optional django-recaptcha and CSRF protection
- **⚡ Background Processing** with Celery for email sending and heavy tasks
- **📖 Auto-Generated API Documentation** with interactive OpenAPI interface
- **🎛️ Enhanced Conditional Logic** with improved rule engine


---

# About

Headless WAF Builder is a comprehensive headless-first extension that enhances Wagtail's built-in Form Builder with:

- **🎛️ Advanced Conditional Logic** - Show/hide fields based on user input with complex rule sets
- **🌐 Headless API Support** - Complete REST API for frontend frameworks and mobile apps
- **📱 Modern Field Types** - Extended field library including phone, date, and custom validation
- **🔧 Developer-Friendly** - Easy integration, comprehensive documentation, and extensible architecture

## 🤔 Why Choose Headless WAF Builder?

| Feature | Headless WAF Builder | Original wagtail-advanced-form-builder |
|---------|---------------------|----------------------------------------|
| **🌐 REST API** | ✅ Complete Django Ninja API | ❌ No API |
| **📱 Frontend Frameworks** | ✅ React, Vue, Angular, Mobile | ❌ Wagtail templates only |
| **🔒 Modern Security** | ✅ CSRF, reCAPTCHA, Rate limiting | ⚠️ Basic |
| **📖 API Documentation** | ✅ Auto-generated OpenAPI docs | ❌ No API docs |
| **⚡ Background Processing** | ✅ Celery integration | ❌ Synchronous only |
| **🎯 Type Safety** | ✅ Pydantic schemas | ❌ No schemas |
| **📊 Headless CMS Ready** | ✅ Built for decoupled architecture | ❌ Traditional Wagtail CMS + Django Templates |

**Choose `headless-waf-builder` if you're building:**
- 🚀 Modern SPA applications (React, Vue, Angular)
- 📱 Mobile apps that need form APIs
- 🌐 Headless/decoupled Wagtail sites
- 🔗 Multi-channel content delivery
- 🎯 API-first applications

---

# 🛠️ Installation & Setup

## Basic Installation

### Production Installation
```bash
pip install headless-waf-builder
```


Add to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... other apps
    'headless_waf_builder',
    # ... 
]
```

> **✨ Modern Architecture**: The new `headless_waf_builder` package follows modern Python packaging standards with `src/` layout and `pyproject.toml` configuration.

## Headless API Setup
```python
# urls.py
from headless_waf_builder.api.router import headless_waf_builder_api

urlpatterns = [
    # ... your existing URLs
    path("api/", headless_waf_builder_api.urls),
]
```

Run migrations:
```bash
./manage.py migrate
```

🎉 After the migration succeed! Your API will be available at `/api/` with documentation at `/api/docs`

---

# 📋 Comprehensive Field Support

### Core Field Types
- **📝 Text Fields** - Single line, multi-line with validation
- **📧 Email Field** - Built-in email validation  
- **🔢 Number Field** - Numeric input with min/max validation
- **📞 Phone Field** - International phone number support
- **📅 Simple Date Field** - Date picker with age validation
- **🔗 URL Field** - URL validation and formatting
- **🙈 Hidden Field** - For tracking and default values

### Advanced Input Types  
- **📋 Dropdown/Select** - Single and multi-select options
- **✅ Checkbox Fields** - Single checkbox and checkbox groups
- **🔘 Radio Buttons** - Single choice with custom layouts
- **🎨 HTML Field** - Rich content and custom markup
- **📱 Responsive Layouts** - Side-by-side and mobile-optimized displays

### 🎯 Conditional Logic Engine
Create dynamic forms with sophisticated show/hide rules:

- **Comparison Operators**: `equals`, `not equals`, `greater than`, `less than`, `contains`
- **String Matching**: `starts with`, `ends with`, `is blank`, `is not blank`
- **Multiple Conditions**: Combine rules with AND/OR logic
- **Cross-Field Dependencies**: Field visibility based on other field values
- **Real-time Updates**: Instant field visibility changes as users interact

---

# 🌐 Headless API Reference

## Endpoints

### `GET /api/form_by_path/{path}`
Retrieve form schema and configuration
```json
{
  "id": 1,
  "title": "Contact Form",
  "fields": [
    {
      "id": 1,
      "type": "singleline", 
      "name": "full_name",
      "label": "Full Name",
      "required": true,
      "rules": {
        "action": "show",
        "conditions": [...]
      }
    }
  ],
  "use_google_recaptcha": true,
  "google_recaptcha_public_key": "..."
}
```

### `POST /api/form_by_path/`
Submit form data with validation
```json
{
  "path": "contact-form",
  "form_fields": {
    "full_name": "John Doe",
    "email": "john@example.com"
  },
  "recaptcha_token": "..."
}
```

### `GET /api/csrf/`
Get CSRF token for secure submissions
```json
{
  "csrftoken": "abc123..."
}
```

---

# 📚 Documentation

The complete documentation is available at [here](https://github.com/octavenz/headless-wagtail-advanced-form-builder/blob/master/docs/index.md)

---

# 🆘 Getting Help

- **🐛 Bug Reports**: [Issue Tracker](https://github.com/octavenz/headless-wagtail-advanced-form-builder/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/octavenz/headless-wagtail-advanced-form-builder/discussions)

# 👥 Authors

* Richard Blake, Dan Brosnan & Vincent Tran ([Octave](https://octave.nz))

# 📄 License

This project is licensed under the BSD License - see the [LICENSE file](./LICENCE) for details

