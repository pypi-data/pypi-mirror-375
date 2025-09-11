# URL Field

A URL input field for collecting and validating web addresses with built-in URL format validation and protocol handling.

## 🎯 Use Cases

- **Website URLs**: Company websites, personal portfolios, blogs
- **Social Media**: LinkedIn profiles, Twitter handles, Facebook pages
- **References**: Portfolio links, previous work examples
- **Resources**: Documentation links, relevant articles
- **Media**: Video links, image galleries, online content
- **Contact**: Website contact pages, booking systems

## 📋 API Response

```json
{
  "id": "website",
  "label": "Website URL",
  "field_type": "url",
  "required": false,
  "help_text": "Enter your website address (e.g., https://example.com)",
  "choices": null,
  "default_value": "",
  "max_length": 200
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"url"` |
| `max_length` | integer | Maximum URL length (default: 200) |
| All standard properties | - | Required, label, help_text, etc. |

## 🔧 Frontend Implementation

### HTML Example
```html
<div class="form-field">
  <label for="website">
    Website URL
  </label>
  <input 
    type="url" 
    id="website" 
    name="website"
    placeholder="https://example.com"
    maxlength="200"
  />
  <small class="help-text">
    Enter your website address (e.g., https://example.com)
  </small>
</div>
```

### React Example
```jsx
const URLField = ({ field, value, onChange, error }) => (
  <div className="form-field">
    <label htmlFor={field.id}>
      {field.label}
      {field.required && <span className="required">*</span>}
    </label>
    <input
      type="url"
      id={field.id}
      name={field.id}
      value={value || field.default_value || ''}
      onChange={(e) => onChange(field.id, e.target.value)}
      maxLength={field.max_length || 200}
      required={field.required}
      placeholder={field.help_text || 'https://example.com'}
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
const validateURLField = (field, value) => {
  const errors = [];
  
  // Required validation
  if (field.required && (!value || value.trim() === '')) {
    errors.push(`${field.label} is required`);
    return errors;
  }
  
  if (value && value.trim() !== '') {
    // URL format validation
    try {
      const url = new URL(value);
      
      // Protocol validation
      if (!['http:', 'https:'].includes(url.protocol)) {
        errors.push('URL must start with http:// or https://');
      }
      
      // Domain validation (basic)
      if (!url.hostname || url.hostname.length < 1) {
        errors.push('Please enter a valid URL with a domain name');
      }
      
    } catch (e) {
      errors.push('Please enter a valid URL (e.g., https://example.com)');
    }
    
    // Max length validation
    if (value.length > (field.max_length || 200)) {
      errors.push(`URL must be ${field.max_length || 200} characters or less`);
    }
  }
  
  return errors;
};
```

### Auto-Protocol Addition
```javascript
const normalizeURL = (value) => {
  if (!value) return value;
  
  const trimmed = value.trim();
  if (trimmed && !trimmed.match(/^https?:\/\//)) {
    return `https://${trimmed}`;
  }
  return trimmed;
};

const URLFieldWithAutoProtocol = ({ field, value, onChange, error }) => {
  const handleBlur = (e) => {
    const normalizedValue = normalizeURL(e.target.value);
    if (normalizedValue !== e.target.value) {
      onChange(field.id, normalizedValue);
    }
  };
  
  return (
    <input
      type="url"
      value={value || ''}
      onChange={(e) => onChange(field.id, e.target.value)}
      onBlur={handleBlur}
      placeholder="example.com (https:// will be added automatically)"
    />
  );
};
```

### Server-Side Validation
The API automatically validates:
- **URL format**: Strict URL validation with protocol requirement
- **Protocol validation**: Ensures http:// or https:// protocols
- **Max length**: Enforces character limits
- **Required fields**: Returns 422 if missing

**Error Response Example:**
```json
{
  "detail": [
    {
      "field": "website",
      "message": "Enter a valid URL."
    }
  ]
}
```

## 🎨 Enhanced Styling

### CSS Base Styles
```css
.form-field input[type="url"] {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  font-family: monospace; /* Better for URLs */
}

.form-field input[type="url"]:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-field input[type="url"]:valid {
  border-color: #10b981;
}

.form-field input[type="url"]:invalid:not(:focus):not(:placeholder-shown) {
  border-color: #ef4444;
}

/* URL input with icon */
.url-input-wrapper {
  position: relative;
}

.url-input-wrapper::before {
  content: "🔗";
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  pointer-events: none;
}

.url-input-wrapper input {
  padding-left: 2.5rem;
}
```

### URL Field with Preview (React)
```jsx
const URLFieldWithPreview = ({ field, value, onChange, error }) => {
  const [isValidURL, setIsValidURL] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const validateURL = (url) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };
  
  useEffect(() => {
    if (value) {
      setIsValidURL(validateURL(value));
    } else {
      setIsValidURL(false);
    }
  }, [value]);
  
  const openPreview = () => {
    if (isValidURL) {
      window.open(value, '_blank', 'noopener,noreferrer');
    }
  };
  
  return (
    <div className="form-field">
      <label htmlFor={field.id}>{field.label}</label>
      <div className="url-input-wrapper">
        <input
          type="url"
          id={field.id}
          name={field.id}
          value={value || ''}
          onChange={(e) => onChange(field.id, e.target.value)}
          placeholder="https://example.com"
        />
        {isValidURL && (
          <button
            type="button"
            className="url-preview-btn"
            onClick={openPreview}
            aria-label="Open URL in new tab"
          >
            🔗
          </button>
        )}
      </div>
      {error && <span className="error">{error}</span>}
    </div>
  );
};
```

### Social Media URL Field
```jsx
const SocialURLField = ({ field, value, onChange, platform = 'website' }) => {
  const platformConfig = {
    website: { 
      icon: '🌐', 
      placeholder: 'https://yourwebsite.com' 
    },
    linkedin: { 
      icon: '💼', 
      placeholder: 'https://linkedin.com/in/username',
      domain: 'linkedin.com' 
    },
    twitter: { 
      icon: '🐦', 
      placeholder: 'https://twitter.com/username',
      domain: 'twitter.com' 
    },
    github: { 
      icon: '🐙', 
      placeholder: 'https://github.com/username',
      domain: 'github.com' 
    }
  };
  
  const config = platformConfig[platform] || platformConfig.website;
  
  const validateDomain = (url) => {
    if (!config.domain) return true;
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.includes(config.domain);
    } catch {
      return false;
    }
  };
  
  return (
    <div className="form-field">
      <label htmlFor={field.id}>
        {config.icon} {field.label}
      </label>
      <input
        type="url"
        id={field.id}
        value={value || ''}
        onChange={(e) => onChange(field.id, e.target.value)}
        placeholder={config.placeholder}
        className={value && !validateDomain(value) ? 'domain-mismatch' : ''}
      />
      {value && config.domain && !validateDomain(value) && (
        <small className="warning">
          This doesn't appear to be a {platform} URL
        </small>
      )}
    </div>
  );
};
```

## 🔄 Conditional Logic

URL fields can trigger conditional logic:

**Example API Response:**
```json
{
  "form_fields": [
    {
      "id": "has_website",
      "label": "Do you have a website?",
      "field_type": "radio",
      "choices": [["yes", "Yes"], ["no", "No"]],
      "required": true
    },
    {
      "id": "website_url",
      "label": "Website URL",
      "field_type": "url",
      "conditional_logic": {
        "action": "show",
        "conditions": [
          {
            "field": "has_website",
            "operator": "equals",
            "value": "yes"
          }
        ]
      }
    }
  ]
}
```

## 🌐 URL Processing

### Extract Domain for Display
```javascript
const extractDomain = (url) => {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.replace('www.', '');
  } catch {
    return url;
  }
};

const URLDisplay = ({ url }) => (
  <div className="url-display">
    <a href={url} target="_blank" rel="noopener noreferrer">
      {extractDomain(url)}
    </a>
  </div>
);
```

### URL Validation with Fetch Check
```javascript
const checkURLAccessibility = async (url) => {
  try {
    const response = await fetch(url, { 
      method: 'HEAD', 
      mode: 'no-cors' 
    });
    return true;
  } catch {
    return false;
  }
};

const URLFieldWithCheck = ({ field, value, onChange }) => {
  const [urlStatus, setUrlStatus] = useState(null);
  
  const checkURL = async () => {
    if (value && validateURL(value)) {
      setUrlStatus('checking');
      const isAccessible = await checkURLAccessibility(value);
      setUrlStatus(isAccessible ? 'accessible' : 'inaccessible');
    }
  };
  
  return (
    <div className="form-field">
      <label>{field.label}</label>
      <div className="url-input-with-check">
        <input
          type="url"
          value={value || ''}
          onChange={(e) => onChange(field.id, e.target.value)}
          onBlur={checkURL}
        />
        {urlStatus === 'checking' && <span>🔄 Checking...</span>}
        {urlStatus === 'accessible' && <span>✅ URL accessible</span>}
        {urlStatus === 'inaccessible' && <span>⚠️ URL may not be accessible</span>}
      </div>
    </div>
  );
};
```

## 📝 Form Submission

When submitting, ensure URLs are properly formatted:

```javascript
const formData = {
  "website": "https://example.com",
  "linkedin": "https://linkedin.com/in/username",
  "portfolio": "https://myportfolio.dev"
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

URL fields provide robust web address validation with enhanced user experience features for collecting and validating website links and online resources.
