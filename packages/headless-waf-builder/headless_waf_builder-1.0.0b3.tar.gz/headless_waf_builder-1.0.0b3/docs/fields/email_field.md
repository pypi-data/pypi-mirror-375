# Email Field

Specialized field for collecting and validating email addresses with built-in email format validation.

## 🎯 Use Cases

- **Contact Forms**: Primary contact email
- **Newsletter Signups**: Subscription emails  
- **User Registration**: Account creation
- **Notifications**: Where to send confirmations
- **Support Requests**: Reply-to addresses

## 📋 API Response

```json
{
  "id": "email",
  "label": "Email Address", 
  "field_type": "email",
  "required": true,
  "help_text": "We'll never share your email address",
  "choices": null,
  "default_value": "",
  "max_length": 254
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"email"` |
| `max_length` | integer | Max chars (default: 254, RFC compliant) |
| All standard field properties | - | Required, label, help_text, etc. |

## 🔧 Frontend Implementation

### HTML Example
```html
<div class="form-field">
  <label for="email">
    Email Address <span class="required">*</span>
  </label>
  <input 
    type="email" 
    id="email" 
    name="email"
    maxlength="254"
    required
    placeholder="Enter your email address"
  />
  <small class="help-text">We'll never share your email address</small>
</div>
```

### React Example  
```jsx
const EmailField = ({ field, value, onChange, error }) => (
  <div className="form-field">
    <label htmlFor={field.id}>
      {field.label}
      {field.required && <span className="required">*</span>}
    </label>
    <input
      type="email"
      id={field.id}
      name={field.id}
      value={value || ''}
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
const validateEmailField = (field, value) => {
  const errors = [];
  
  // Required validation
  if (field.required && (!value || value.trim() === '')) {
    errors.push(`${field.label} is required`);
    return errors;
  }
  
  if (value) {
    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      errors.push('Please enter a valid email address');
    }
    
    // Max length validation
    if (value.length > field.max_length) {
      errors.push(`Email address must be ${field.max_length} characters or less`);
    }
  }
  
  return errors;
};
```

### Server-Side Validation
The API automatically validates:
- **Email format**: Strict RFC 5322 compliance
- **Required fields**: Returns 422 if missing
- **Max length**: Enforces 254 character limit

**Error Response Example:**
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

## 📧 Email Form Integration

When used in **EmailFormPage**, this field can serve special purposes:

### Auto-Reply Configuration
```json
{
  "email_settings": {
    "send_auto_reply": true,
    "auto_reply_subject": "Thank you for contacting us"
  }
}
```

The system can automatically send confirmation emails to the submitted email address.

### Multiple Email Fields
```json
{
  "form_fields": [
    {
      "id": "primary_email",
      "label": "Primary Email",
      "field_type": "email",
      "required": true
    },
    {
      "id": "backup_email", 
      "label": "Backup Email",
      "field_type": "email",
      "required": false
    }
  ]
}
```

## 🔄 Advanced Usage

### Email Verification (Frontend)
```javascript
const EmailFieldWithVerification = ({ field, value, onChange }) => {
  const [isVerifying, setIsVerifying] = useState(false);
  const [isValid, setIsValid] = useState(null);
  
  const verifyEmail = async (email) => {
    setIsVerifying(true);
    try {
      // Optional: Add email verification service
      const response = await fetch(`/api/verify-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      setIsValid(response.ok);
    } catch (error) {
      setIsValid(false);
    } finally {
      setIsVerifying(false);
    }
  };
  
  return (
    <div className="form-field">
      <label htmlFor={field.id}>{field.label}</label>
      <div className="email-input-wrapper">
        <input
          type="email"
          id={field.id}
          value={value || ''}
          onChange={(e) => {
            onChange(field.id, e.target.value);
            setIsValid(null);
          }}
          onBlur={() => value && verifyEmail(value)}
        />
        {isVerifying && <span className="verifying">Verifying...</span>}
        {isValid === true && <span className="valid">✓ Valid</span>}
        {isValid === false && <span className="invalid">✗ Invalid</span>}
      </div>
    </div>
  );
};
```

### Conditional Email Logic
```json
{
  "id": "business_email",
  "label": "Business Email",
  "field_type": "email", 
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

## 🎨 Enhanced Styling

```css
.form-field input[type="email"] {
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;
  padding-right: 2.5rem;
}

.email-input-wrapper {
  position: relative;
}

.verifying, .valid, .invalid {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.875rem;
}

.valid { color: #10b981; }
.invalid { color: #ef4444; }
.verifying { color: #6b7280; }
```

Email fields provide robust validation and seamless integration with email-sending functionality, making them essential for contact forms and user communication.
