# Quick Start Guide

Get up and running with headless forms in minutes using the built-in page types.

## 🏗️ Creating Your First Form

### 1. Access Wagtail Admin
- Navigate to `http://localhost:8000/admin`
- Login with: `admin` / `admin123` (Docker setup)

### 2. Create a Form Page

**Option A: Basic Form**
```python
# In Wagtail admin, create a new FormPage
- Choose "Form Page" from the page types
- Add your form fields using the intuitive field builder
- Configure conditional logic if needed
- Publish the page
```

**Option B: Email Form**  
```python
# For forms that send email notifications
- Choose "Email Form Page" from the page types  
- Configure email settings (to/from addresses)
- Build your form with the visual editor
- Set up email templates
- Publish the page
```

## 🎯 Built-in Page Types

### FormPage
A basic form that stores submissions in the database.

**Features:**
- ✅ Form submission storage
- ✅ reCAPTCHA integration
- ✅ Conditional field logic
- ✅ REST API endpoints
- ✅ Custom validation

**API Endpoints:**
- `GET /api/form_by_path/{path}` - Get form definition
- `POST /api/form_by_path/` - Submit form data

### EmailFormPage  
Extends FormPage with automatic email notifications.

**Additional Features:**
- ✅ Automatic email sending
- ✅ Customizable email templates
- ✅ Multiple recipient support
- ✅ Email template variables

**Email Configuration:**
```python
# In Wagtail admin
from_address = "noreply@yoursite.com"
to_address = "admin@yoursite.com"  
subject = "New Form Submission"
```

## 🚀 Using the REST API

### 1. Get Form Definition
```bash
curl -X GET "http://localhost:8000/api/form_by_path/contact-form" \
  -H "Accept: application/json"
```

**Response:**
```json
{
  "id": 1,
  "title": "Contact Form",
  "slug": "contact-form", 
  "url_path": "/contact-form/",
  "form_fields": [
    {
      "id": "name",
      "label": "Your Name",
      "field_type": "singleline",
      "required": true
    }
  ]
}
```

### 2. Submit Form Data
```bash
curl -X POST "http://localhost:8000/api/form_by_path/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -d '{
    "path": "/contact-form/",
    "form_data": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

## 🔧 Frontend Integration Examples

### React/Next.js
```javascript
// Get form definition
const form = await fetch('/api/form_by_path/contact-form')
  .then(res => res.json());

// Submit form
const response = await fetch('/api/form_by_path/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    path: '/contact-form/',
    form_data: formData
  })
});
```

## 🎨 Advanced Features

### Conditional Logic
Create dynamic forms where field visibility depends on other field values:

```python
# In Wagtail admin, configure conditional rules:
- IF "contact_method" EQUALS "email" 
- THEN SHOW "email_address" field
- ELSE HIDE "email_address" field
```

### reCAPTCHA Integration
Enable bot protection:
1. Check "Use Google reCAPTCHA" in the form settings
2. Add reCAPTCHA keys to your environment variables
3. Frontend handles reCAPTCHA token generation

## 📝 Next Steps

- [Explore all field types](../fields/basic_field.md)
- [Read the complete API documentation](../headless/api.md)
- [Learn about custom page models](using_your_own_page_models.md)
            
