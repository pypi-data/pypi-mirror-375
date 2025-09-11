# Hidden Field

A hidden input field for storing data that's not visible to users but is included in form submissions. Essential for tracking, security, and passing context data.

## 🎯 Use Cases

- **Form Context**: Form IDs, page references, source tracking
- **Security**: CSRF tokens, nonce values, verification codes
- **Analytics**: UTM parameters, referral sources, campaign tracking
- **State Management**: Previous form values, workflow steps
- **API Integration**: External system IDs, correlation tokens
- **User Context**: User IDs, session identifiers (when safe)

## 📋 API Response

```json
{
  "id": "form_source",
  "label": "Form Source",
  "field_type": "hidden",
  "required": false,
  "help_text": "",
  "choices": null,
  "default_value": "website_contact_form",
  "max_length": 255
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"hidden"` |
| `default_value` | string | The hidden value to submit |
| `max_length` | integer | Maximum value length |
| All standard properties | - | Label (for admin), help_text (for documentation) |

**Note**: Hidden fields typically have `required: false` and are populated programmatically.

## 🔧 Frontend Implementation

### HTML Example
```html
<input 
  type="hidden" 
  id="form_source" 
  name="form_source"
  value="website_contact_form"
/>
```

### React Example
```jsx
const HiddenField = ({ field, value, onChange }) => (
  <input
    type="hidden"
    id={field.id}
    name={field.id}
    value={value || field.default_value || ''}
    onChange={(e) => onChange(field.id, e.target.value)}
  />
);

// Advanced hidden field with dynamic value
const DynamicHiddenField = ({ field, value, onChange }) => {
  useEffect(() => {
    // Set dynamic values based on context
    const contextValue = getContextValue(field.id);
    if (contextValue && !value) {
      onChange(field.id, contextValue);
    }
  }, [field.id, value, onChange]);
  
  return (
    <input
      type="hidden"
      id={field.id}
      name={field.id}
      value={value || field.default_value || ''}
      readOnly
    />
  );
};

const getContextValue = (fieldId) => {
  switch (fieldId) {
    case 'referrer':
      return document.referrer;
    case 'timestamp':
      return Date.now().toString();
    case 'user_agent':
      return navigator.userAgent;
    case 'page_url':
      return window.location.href;
    default:
      return null;
  }
};
```

## ✅ Validation

### Client-Side Validation
```javascript
const validateHiddenField = (field, value) => {
  const errors = [];
  
  // Hidden fields are rarely required, but validate if they are
  if (field.required && (!value || value.trim() === '')) {
    errors.push(`Hidden field ${field.id} is required`);
  }
  
  // Max length validation
  if (value && value.length > (field.max_length || 255)) {
    errors.push(`Hidden field ${field.id} exceeds maximum length`);
  }
  
  return errors;
};
```

### Server-Side Validation
The API validates hidden fields for:
- **Data integrity**: Ensures values haven't been tampered with
- **Max length**: Enforces character limits
- **Required fields**: If configured as required
- **Format validation**: Based on field purpose

**Note**: Never trust hidden field values for security decisions - always validate server-side.

## 🔒 Security Considerations

### Safe Hidden Field Usage
```javascript
// ✅ SAFE - Tracking and analytics data
const safeHiddenFields = {
  form_source: 'contact_page',
  utm_campaign: 'spring_2024',
  referrer_url: document.referrer,
  timestamp: Date.now().toString()
};

// ❌ UNSAFE - Sensitive data that could be manipulated
const unsafeHiddenFields = {
  user_id: '12345',           // User could change this
  admin_access: 'true',       // Security bypass attempt
  price: '100.00',           // User could modify pricing
  is_premium: 'true'         // Privilege escalation
};
```

### Secure Hidden Field Implementation
```jsx
const SecureHiddenField = ({ field, value, onChange }) => {
  // Only allow specific, safe hidden fields
  const allowedHiddenFields = [
    'form_source',
    'utm_campaign', 
    'referrer',
    'timestamp',
    'form_version'
  ];
  
  if (!allowedHiddenFields.includes(field.id)) {
    console.warn(`Hidden field ${field.id} not in allowed list`);
    return null;
  }
  
  return (
    <input
      type="hidden"
      id={field.id}
      name={field.id}
      value={value || field.default_value || ''}
      readOnly
    />
  );
};
```

## 🛠️ Common Hidden Field Patterns

### Analytics and Tracking
```jsx
const AnalyticsHiddenFields = ({ onChange }) => {
  useEffect(() => {
    // Set analytics data
    onChange('page_url', window.location.href);
    onChange('referrer', document.referrer);
    onChange('timestamp', new Date().toISOString());
    onChange('session_id', getSessionId());
    
    // UTM parameters
    const urlParams = new URLSearchParams(window.location.search);
    onChange('utm_source', urlParams.get('utm_source') || '');
    onChange('utm_medium', urlParams.get('utm_medium') || '');
    onChange('utm_campaign', urlParams.get('utm_campaign') || '');
  }, [onChange]);
  
  return null; // These are set programmatically
};
```

### Form Context
```jsx
const FormContextFields = ({ formType, formVersion, onChange }) => {
  useEffect(() => {
    onChange('form_type', formType);
    onChange('form_version', formVersion);
    onChange('browser_info', getBrowserInfo());
  }, [formType, formVersion, onChange]);
  
  return null;
};

const getBrowserInfo = () => {
  return {
    user_agent: navigator.userAgent,
    language: navigator.language,
    screen_resolution: `${screen.width}x${screen.height}`,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  };
};
```

### A/B Testing
```jsx
const ABTestHiddenFields = ({ onChange }) => {
  useEffect(() => {
    // Determine A/B test variant
    const variant = Math.random() < 0.5 ? 'A' : 'B';
    onChange('ab_test_variant', variant);
    
    // Set test parameters
    onChange('experiment_id', 'contact_form_test_2024');
    onChange('user_cohort', getUserCohort());
  }, [onChange]);
  
  return null;
};
```

## 🔄 Dynamic Hidden Fields

### Context-Aware Hidden Fields
```jsx
const ContextHiddenFields = ({ user, page, onChange }) => {
  useEffect(() => {
    // User context (if available and safe)
    if (user?.isLoggedIn) {
      onChange('user_type', user.accountType);
      onChange('user_tier', user.subscriptionTier);
    }
    
    // Page context
    onChange('page_section', page.section);
    onChange('form_location', page.formLocation);
    
    // Technical context
    onChange('viewport_size', `${window.innerWidth}x${window.innerHeight}`);
    onChange('device_type', getDeviceType());
  }, [user, page, onChange]);
  
  return null;
};

const getDeviceType = () => {
  const width = window.innerWidth;
  if (width < 768) return 'mobile';
  if (width < 1024) return 'tablet';
  return 'desktop';
};
```

## 📊 Hidden Field Validation in Forms

### Form-Level Hidden Field Management
```jsx
const FormWithHiddenFields = ({ formSchema, onSubmit }) => {
  const [formData, setFormData] = useState({});
  
  const updateField = (fieldId, value) => {
    setFormData(prev => ({ ...prev, [fieldId]: value }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Add automatic hidden fields
    const hiddenData = {
      submission_timestamp: new Date().toISOString(),
      form_session_duration: getSessionDuration(),
      form_submission_method: 'api'
    };
    
    onSubmit({ ...formData, ...hiddenData });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {formSchema.form_fields.map(field => {
        if (field.field_type === 'hidden') {
          return (
            <HiddenField
              key={field.id}
              field={field}
              value={formData[field.id]}
              onChange={updateField}
            />
          );
        }
        // Render other field types...
      })}
      
      <AnalyticsHiddenFields onChange={updateField} />
      <button type="submit">Submit</button>
    </form>
  );
};
```

## 📝 Form Submission

Hidden fields are included in form submissions automatically:

```javascript
const formData = {
  // Visible field data
  "name": "John Doe",
  "email": "john@example.com",
  
  // Hidden field data
  "form_source": "website_contact_form",
  "utm_campaign": "spring_2024",
  "referrer": "https://google.com",
  "timestamp": "2024-01-15T10:30:00Z",
  "form_version": "2.1",
  "user_agent": "Mozilla/5.0...",
  "page_url": "https://example.com/contact"
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

## ⚠️ Best Practices

### DO:
- ✅ Use for tracking and analytics
- ✅ Store form context and metadata
- ✅ Include timestamp and version info
- ✅ Validate all hidden field data server-side
- ✅ Keep values non-sensitive

### DON'T:
- ❌ Store sensitive user data
- ❌ Use for security decisions
- ❌ Trust values for authorization
- ❌ Include personal information
- ❌ Store large amounts of data

Hidden fields are powerful tools for form context and tracking while maintaining clean user interfaces, but must be used securely and validated properly on the server side.


