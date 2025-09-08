# REST API Documentation

Complete reference for the Headless Wagtail Advanced Form Builder REST API.

## 🔗 Base URL
- Local Development: `http://localhost:8000/api/`
- Production: `https://yoursite.com/api/`

## 📖 Interactive Documentation
Visit `/api/docs` for interactive Swagger/OpenAPI documentation with live testing capabilities.

---

## 🔐 Authentication & Security

### CSRF Protection
All POST requests require a valid CSRF token.

**Get CSRF Token:**
```bash
GET /api/csrf/
```

**Response:**
```json
{
  "csrftoken": "abc123xyz..."
}
```

**Include in requests:**
```bash
curl -X POST "/api/form_by_path/" \
  -H "X-CSRFToken: abc123xyz..." \
  -d "..."
```

### reCAPTCHA (Optional)
Forms with reCAPTCHA enabled require a valid token in submissions.

---

## 📋 Endpoints

### 1. Get Form by Path

Retrieve form definition and metadata by URL path.

```http
GET /api/form_by_path/{path}
```

**Parameters:**
- `path` (string): The URL path of the form (e.g., "contact-form")

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/form_by_path/contact-form"
```

**Example Response:**
```json
{
  "id": 1,
  "title": "Contact Form",
  "slug": "contact-form",
  "url_path": "/contact-form/",
  "meta": {
    "type": "headless_waf_builder.FormPage",
    "detail_url": "http://localhost:8000/api/form_by_path/contact-form"
  },
  "form_fields": [
    {
      "id": "name",
      "label": "Your Name", 
      "field_type": "singleline",
      "required": true,
      "help_text": "Enter your full name",
      "choices": null,
      "default_value": "",
      "max_length": 255
    },
    {
      "id": "email",
      "label": "Email Address",
      "field_type": "email", 
      "required": true,
      "help_text": "We'll never share your email",
      "choices": null,
      "default_value": "",
      "max_length": 254
    }
  ],
  "submit_button_text": "Send Message",
  "thanks_page_title": "Thank You!",
  "thanks_page_content": "<p>Your message has been sent.</p>",
  "use_google_recaptcha": false
}
```

**Response Codes:**
- `200` - Form found and returned
- `404` - No form found with specified path
- `500` - Multiple forms found (path too generic)

### 2. Submit Form Data

Submit form data for processing.

```http
POST /api/form_by_path/
```

**Request Body:**
```json
{
  "path": "/contact-form/",
  "form_data": {
    "name": "John Doe",
    "email": "john@example.com", 
    "message": "Hello world!"
  }
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/form_by_path/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: abc123xyz..." \
  -d '{
    "path": "/contact-form/",
    "form_data": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

**Success Response (204):**
```json
{
  "message": "Form submitted successfully",
  "thanks_page": {
    "title": "Thank You!",
    "content": "<p>Your message has been sent.</p>"
  }
}
```

**Error Responses:**

**403 - CSRF Error:**
```json
{
  "message": "CSRF validation failed. Please refresh the page and try again."
}
```

**404 - Form Not Found:**
```json
{
  "message": "No form found with the specified path"
}
```

**422 - Validation Error:**
```json
{
  "detail": [
    {
      "field": "email",
      "message": "Enter a valid email address."
    }
  ]
}
```

**500 - Server Error:**
```json
{
  "message": "Found 2 forms with that path. Please use a more specific path."
}
```

---

## 🎯 Field Types Reference

### Basic Fields
- `singleline` - Single line text input
- `multiline` - Multi-line textarea
- `email` - Email input with validation
- `url` - URL input with validation  
- `number` - Numeric input
- `phone` - Phone number input
- `date` - Date picker

### Choice Fields
- `dropdown` - Select dropdown
- `radio` - Radio button group
- `checkboxes` - Multiple checkboxes
- `multiselect` - Multi-select dropdown

### Special Fields
- `checkbox` - Single checkbox
- `hidden` - Hidden input field
- `html` - HTML content (display only)

---

## 🔄 Conditional Logic

Forms support conditional field visibility based on other field values.

**Example Form Response with Conditions:**
```json
{
  "form_fields": [
    {
      "id": "contact_method",
      "label": "Preferred Contact Method",
      "field_type": "radio",
      "choices": ["email", "phone"],
      "required": true
    },
    {
      "id": "email_address", 
      "label": "Email",
      "field_type": "email",
      "required": true,
      "conditional_logic": {
        "action": "show",
        "conditions": [
          {
            "field": "contact_method",
            "operator": "equals", 
            "value": "email"
          }
        ]
      }
    }
  ]
}
```

**Frontend Implementation:**
Your frontend should implement the conditional logic by:
1. Monitoring field value changes
2. Evaluating conditions for each field
3. Showing/hiding fields accordingly
4. Applying validation only to visible, required fields

---

## 📧 Email Forms

EmailFormPage includes additional email configuration:

**Additional Response Fields:**
```json
{
  "email_settings": {
    "from_address": "noreply@example.com",
    "to_address": "admin@example.com", 
    "subject": "New Contact Form Submission"
  }
}
```

When submitted, EmailFormPage automatically:
1. Validates and stores the submission
2. Sends email notification to configured address
3. Returns the thanks page content

---

## 🛡️ Security Features

### Rate Limiting
API endpoints include built-in rate limiting to prevent abuse.

### Input Validation
- All fields validated according to their type
- XSS protection on all inputs
- SQL injection prevention
- File upload restrictions (if applicable)

### CORS Configuration
Configure CORS headers for frontend integration:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "https://yourfrontend.com"
]
```

---

## 🧪 Testing

### Using curl
```bash
# Test form retrieval
curl -X GET "http://localhost:8000/api/form_by_path/test-form"

# Test form submission
curl -X POST "http://localhost:8000/api/form_by_path/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $(curl -s http://localhost:8000/api/csrf/ | jq -r .csrftoken)" \
  -d '{"path": "/test-form/", "form_data": {"name": "Test User"}}'
```

### Using JavaScript Fetch
```javascript
// Get CSRF token
const { csrftoken } = await fetch('/api/csrf/').then(r => r.json());

// Submit form
const response = await fetch('/api/form_by_path/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrftoken
  },
  body: JSON.stringify({
    path: '/contact-form/',
    form_data: { name: 'John', email: 'john@example.com' }
  })
});
```

---

## 📊 Error Handling

Always check response status codes and handle errors appropriately:

```javascript
const submitForm = async (formData) => {
  try {
    const response = await fetch('/api/form_by_path/', {
      method: 'POST',
      headers: { /* ... */ },
      body: JSON.stringify(formData)
    });
    
    if (response.status === 422) {
      const errors = await response.json();
      // Handle validation errors
      return { success: false, errors: errors.detail };
    }
    
    if (response.status === 204) {
      const result = await response.json();
      // Handle success
      return { success: true, thanksPage: result.thanks_page };
    }
    
    // Handle other errors
    throw new Error(`HTTP ${response.status}`);
    
  } catch (error) {
    console.error('Form submission error:', error);
    return { success: false, error: error.message };
  }
};
```
