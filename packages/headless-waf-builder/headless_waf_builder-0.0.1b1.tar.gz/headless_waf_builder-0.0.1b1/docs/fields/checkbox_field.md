# Checkbox Field (Single Checkbox)

A single checkbox field for boolean (true/false) values, agreements, confirmations, and opt-ins.

## 🎯 Use Cases

- **Agreements**: Terms of service, privacy policy acceptance
- **Opt-ins**: Newsletter subscriptions, marketing communications
- **Confirmations**: "I am over 18", "I agree to the terms"
- **Preferences**: "Remember me", "Send notifications"
- **Boolean Settings**: Any true/false choice

## 📋 API Response

```json
{
  "id": "terms_accepted",
  "label": "Terms and Conditions",
  "field_type": "checkbox",
  "required": true,
  "help_text": "I agree to the terms and conditions",
  "choices": null,
  "default_value": false,
  "display_checkbox_label": true
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"checkbox"` |
| `default_value` | boolean | Default checked state (true/false) |
| `display_checkbox_label` | boolean | Show label above checkbox |
| All standard properties | - | Required, label, help_text, etc. |

**Note**: For checkbox fields, the `help_text` often serves as the clickable label next to the checkbox.

## 🔧 Frontend Implementation

### HTML Example
```html
<div class="form-field">
  <!-- Optional: Display field label above -->
  <label class="field-label">Terms and Conditions</label>
  
  <div class="checkbox-wrapper">
    <input 
      type="checkbox" 
      id="terms_accepted" 
      name="terms_accepted"
      required
    />
    <label for="terms_accepted" class="checkbox-label">
      I agree to the terms and conditions
    </label>
  </div>
</div>
```

### React Example
```jsx
const CheckboxField = ({ field, value, onChange, error }) => (
  <div className="form-field">
    {field.display_checkbox_label && (
      <label className="field-label">
        {field.label}
        {field.required && <span className="required">*</span>}
      </label>
    )}
    
    <div className="checkbox-wrapper">
      <input
        type="checkbox"
        id={field.id}
        name={field.id}
        checked={value || field.default_value || false}
        onChange={(e) => onChange(field.id, e.target.checked)}
        required={field.required}
      />
      <label htmlFor={field.id} className="checkbox-label">
        {field.help_text || field.label}
      </label>
    </div>
    
    {error && <span className="error">{error}</span>}
  </div>
);
```

### Vue Example  
```vue
<template>
  <div class="form-field">
    <label v-if="field.display_checkbox_label" class="field-label">
      {{ field.label }}
      <span v-if="field.required" class="required">*</span>
    </label>
    
    <div class="checkbox-wrapper">
      <input
        :id="field.id"
        :name="field.id"
        type="checkbox"
        :checked="modelValue || field.default_value || false"
        @change="$emit('update:modelValue', $event.target.checked)"
        :required="field.required"
      />
      <label :for="field.id" class="checkbox-label">
        {{ field.help_text || field.label }}
      </label>
    </div>
    
    <span v-if="error" class="error">{{ error }}</span>
  </div>
</template>
```

## ✅ Validation

### Client-Side Validation
```javascript
const validateCheckboxField = (field, value) => {
  const errors = [];
  
  // Required validation (must be checked)
  if (field.required && !value) {
    errors.push(`You must accept the ${field.label}`);
  }
  
  return errors;
};
```

### Server-Side Validation
The API automatically validates:
- **Required checkboxes**: Must be `true` if required
- **Boolean values**: Accepts `true`, `false`, or boolean strings
- **Data type**: Converts to proper boolean

**Error Response Example:**
```json
{
  "detail": [
    {
      "field": "terms_accepted",
      "message": "This field is required."
    }
  ]
}
```

## 🎨 Styling Examples

### CSS Base Styles
```css
.checkbox-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.checkbox-wrapper input[type="checkbox"] {
  margin: 0;
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  margin-top: 0.125rem; /* Align with first line of text */
}

.checkbox-label {
  font-size: 0.875rem;
  line-height: 1.25rem;
  cursor: pointer;
  user-select: none;
}

.field-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

/* Custom checkbox styling */
.custom-checkbox {
  position: relative;
  display: inline-block;
}

.custom-checkbox input {
  opacity: 0;
  position: absolute;
}

.custom-checkbox .checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 1rem;
  width: 1rem;
  background-color: #fff;
  border: 2px solid #d1d5db;
  border-radius: 0.25rem;
}

.custom-checkbox input:checked ~ .checkmark {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.custom-checkbox .checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 0.25rem;
  top: 0.125rem;
  width: 0.25rem;
  height: 0.5rem;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.custom-checkbox input:checked ~ .checkmark:after {
  display: block;
}
```

### Custom Styled Checkbox (React)
```jsx
const CustomCheckbox = ({ field, value, onChange, error }) => {
  const isChecked = value || field.default_value || false;
  
  return (
    <div className="form-field">
      <div 
        className={`custom-checkbox ${isChecked ? 'checked' : ''}`}
        onClick={() => onChange(field.id, !isChecked)}
      >
        <input
          type="checkbox"
          id={field.id}
          name={field.id}
          checked={isChecked}
          onChange={(e) => onChange(field.id, e.target.checked)}
          required={field.required}
        />
        <span className="checkmark">
          {isChecked && <CheckIcon />}
        </span>
        <label htmlFor={field.id} className="checkbox-label">
          {field.help_text || field.label}
        </label>
      </div>
      {error && <span className="error">{error}</span>}
    </div>
  );
};
```

## 🔄 Conditional Logic

Checkboxes can trigger conditional logic based on their checked state:

**Example API Response:**
```json
{
  "form_fields": [
    {
      "id": "subscribe_newsletter",
      "label": "Newsletter Subscription",
      "field_type": "checkbox",
      "help_text": "Yes, I want to receive newsletters"
    },
    {
      "id": "email_frequency",
      "label": "Email Frequency",
      "field_type": "dropdown",
      "choices": [["weekly", "Weekly"], ["monthly", "Monthly"]],
      "conditional_logic": {
        "action": "show",
        "conditions": [
          {
            "field": "subscribe_newsletter",
            "operator": "equals",
            "value": true
          }
        ]
      }
    }
  ]
}
```

### Frontend Logic Implementation
```javascript
const shouldShowField = (field, formData) => {
  if (!field.conditional_logic) return true;
  
  return field.conditional_logic.conditions.every(condition => {
    const fieldValue = formData[condition.field];
    
    switch (condition.operator) {
      case 'equals':
        // Handle boolean comparison
        return fieldValue === condition.value;
      case 'is_checked':
        return fieldValue === true;
      case 'is_not_checked':
        return fieldValue !== true;
      default:
        return true;
    }
  });
};
```

## 📱 Accessibility

### Enhanced Accessibility
```jsx
const AccessibleCheckbox = ({ field, value, onChange, error }) => (
  <div className="form-field" role="group" aria-labelledby={`${field.id}-label`}>
    <div className="checkbox-wrapper">
      <input
        type="checkbox"
        id={field.id}
        name={field.id}
        checked={value || false}
        onChange={(e) => onChange(field.id, e.target.checked)}
        required={field.required}
        aria-describedby={field.help_text ? `${field.id}-help` : undefined}
        aria-invalid={error ? 'true' : 'false'}
      />
      <label 
        htmlFor={field.id} 
        id={`${field.id}-label`}
        className="checkbox-label"
      >
        {field.help_text || field.label}
      </label>
    </div>
    
    {field.help_text && field.help_text !== field.label && (
      <small id={`${field.id}-help`} className="help-text">
        {field.help_text}
      </small>
    )}
    
    {error && (
      <span className="error" role="alert" aria-live="polite">
        {error}
      </span>
    )}
  </div>
);
```

## 📝 Form Submission

When submitting, checkbox values are sent as booleans:

```javascript
const formData = {
  "terms_accepted": true,
  "subscribe_newsletter": false,
  "marketing_consent": true
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

Checkbox fields are essential for legal compliance, user preferences, and any boolean choices in forms. They provide clear yes/no options with proper validation and accessibility support.


