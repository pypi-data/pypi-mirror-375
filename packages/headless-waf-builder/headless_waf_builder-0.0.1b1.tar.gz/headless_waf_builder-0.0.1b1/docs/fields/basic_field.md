# Basic Field (Single Line Text)

The most fundamental field type for collecting single-line text input from users.

## 🎯 Use Cases

- **Names**: First name, last name, full name
- **Short Text**: Titles, subject lines, usernames
- **IDs**: Order numbers, reference codes for product, item
- **Simple Input**: Any short text that doesn't require multiple lines

## 📋 API Response

When you fetch a form via the REST API, a basic field appears as:

```json
{
  "id": "first_name",
  "label": "First Name",
  "field_type": "singleline",
  "required": true,
  "help_text": "Enter your first name",
  "choices": null,
  "default_value": "",
  "max_length": 255
}
```

## ⚙️ Configuration Options

### In Wagtail Admin

- **Label**: The display name for the field
- **Required**: Whether the field must be filled
- **Help Text**: Additional guidance for users
- **Default Value**: Pre-filled value (optional)
- **Max Length**: Character limit (default: 255)

### API Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Clean field name for form data |
| `label` | string | Display text for the field |
| `field_type` | string | Always `"singleline"` |
| `required` | boolean | Validation requirement |
| `help_text` | string | Optional help text |
| `max_length` | integer | Maximum character length |
| `default_value` | string | Pre-filled value |

## 🔧 Frontend Implementation

### HTML Example
```html
<div class="form-field">
  <label for="first_name">
    First Name
    <span class="required">*</span>
  </label>
  <input 
    type="text" 
    id="first_name" 
    name="first_name" 
    maxlength="255"
    required
    placeholder="Enter your first name"
  />
  <small class="help-text">Enter your first name</small>
</div>
```

### React Example
```jsx
const BasicField = ({ field, value, onChange, error }) => (
  <div className="form-field">
    <label htmlFor={field.id}>
      {field.label}
      {field.required && <span className="required">*</span>}
    </label>
    <input
      type="text"
      id={field.id}
      name={field.id}
      value={value || field.default_value || ''}
      onChange={(e) => onChange(field.id, e.target.value)}
      maxLength={field.max_length}
      required={field.required}
      placeholder={field.help_text}
    />
    {field.help_text && (
      <small className="help-text">{field.help_text}</small>
    )}
    {error && <span className="error">{error}</span>}
  </div>
);
```

## ✅ Validation

### Client-Side Validation
```javascript
const validateBasicField = (field, value) => {
  const errors = [];
  
  // Required validation
  if (field.required && (!value || value.trim() === '')) {
    errors.push(`${field.label} is required`);
  }
  
  // Max length validation
  if (value && value.length > field.max_length) {
    errors.push(`${field.label} must be ${field.max_length} characters or less`);
  }
  
  return errors;
};
```

### Server-Side Validation
The API automatically validates:
- **Required fields**: Returns 422 error if missing
- **Max length**: Enforces character limits
- **Data type**: Ensures string input

**Error Response Example:**
```json
{
  "detail": [
    {
      "field": "first_name",
      "message": "This field is required."
    }
  ]
}
```

## 🎨 Styling Examples

### CSS Base Styles
```css
.form-field {
  margin-bottom: 1rem;
}

.form-field label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.form-field input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.form-field input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.required {
  color: #ef4444;
}

.help-text {
  color: #6b7280;
  font-size: 0.875rem;
}

.error {
  color: #ef4444;
  font-size: 0.875rem;
}
```

## 🔄 Conditional Logic

Basic fields can be used in conditional logic rules:

**Example API Response with Conditions:**
```json
{
  "id": "company_name",
  "label": "Company Name",
  "field_type": "singleline",
  "required": true,
  "conditional_logic": {
    "action": "show",
    "conditions": [
      {
        "field": "contact_type",
        "operator": "equals",
        "value": "business"
      }
    ]
  }
}
```

**Frontend Logic:**
```javascript
const shouldShowField = (field, formData) => {
  if (!field.conditional_logic) return true;
  
  return field.conditional_logic.conditions.every(condition => {
    const fieldValue = formData[condition.field];
    
    switch (condition.operator) {
      case 'equals':
        return fieldValue === condition.value;
      case 'not_equals':
        return fieldValue !== condition.value;
      case 'contains':
        return fieldValue && fieldValue.includes(condition.value);
      default:
        return true;
    }
  });
};
```

## 📝 Form Submission

When submitting the form, include the field value in the `form_data` object:

```javascript
const formData = {
  "first_name": "John",
  "last_name": "Doe"
};

fetch('/api/form_by_path/', {
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

Basic fields are the foundation of form building and work seamlessly with all other field types and conditional logic.


