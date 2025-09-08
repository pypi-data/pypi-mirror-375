# Multi-Line Field (Textarea)

A textarea field for collecting longer text input that spans multiple lines, such as messages, descriptions, and comments.

## 🎯 Use Cases

- **Messages**: Contact form messages, feedback, inquiries
- **Descriptions**: Product descriptions, project details, requirements
- **Comments**: User comments, reviews, testimonials
- **Content**: Blog posts, articles, long-form text
- **Addresses**: Full postal addresses with multiple lines

## 📋 API Response

```json
{
  "id": "message",
  "label": "Your Message",
  "field_type": "multiline",
  "required": true,
  "help_text": "Please provide details about your inquiry",
  "choices": null,
  "default_value": "",
  "max_length": 1000
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"multiline"` |
| `max_length` | integer | Maximum character count (default varies) |
| All standard properties | - | Required, label, help_text, etc. |

## 🔧 Frontend Implementation

### HTML Example
```html
<div class="form-field">
  <label for="message">
    Your Message <span class="required">*</span>
  </label>
  <textarea 
    id="message" 
    name="message"
    rows="5"
    maxlength="1000"
    placeholder="Please provide details about your inquiry"
    required
  ></textarea>
  <small class="help-text">
    Please provide details about your inquiry
  </small>
  <small class="char-count">0 / 1000 characters</small>
</div>
```

### React Example
```jsx
const MultiLineField = ({ field, value, onChange, error }) => {
  const currentLength = (value || '').length;
  const maxLength = field.max_length || 1000;
  
  return (
    <div className="form-field">
      <label htmlFor={field.id}>
        {field.label}
        {field.required && <span className="required">*</span>}
      </label>
      <textarea
        id={field.id}
        name={field.id}
        value={value || field.default_value || ''}
        onChange={(e) => onChange(field.id, e.target.value)}
        maxLength={maxLength}
        required={field.required}
        placeholder={field.help_text}
        rows={5}
      />
      {field.help_text && (
        <small className="help-text">{field.help_text}</small>
      )}
      <div className="field-footer">
        <small className="char-count">
          {currentLength} / {maxLength} characters
        </small>
        {error && <span className="error">{error}</span>}
      </div>
    </div>
  );
};
```

## ✅ Validation

### Client-Side Validation
```javascript
const validateMultiLineField = (field, value) => {
  const errors = [];
  
  // Required validation
  if (field.required && (!value || value.trim() === '')) {
    errors.push(`${field.label} is required`);
  }
  
  if (value) {
    // Max length validation
    if (value.length > field.max_length) {
      errors.push(`${field.label} must be ${field.max_length} characters or less`);
    }
    
    // Min length validation (if configured)
    if (field.min_length && value.length < field.min_length) {
      errors.push(`${field.label} must be at least ${field.min_length} characters`);
    }
  }
  
  return errors;
};
```

### Server-Side Validation
The API automatically validates:
- **Required fields**: Returns 422 error if empty
- **Max length**: Enforces character limits
- **Data type**: Ensures string input
- **Content filtering**: Basic XSS protection

**Error Response Example:**
```json
{
  "detail": [
    {
      "field": "message",
      "message": "Ensure this field has no more than 1000 characters."
    }
  ]
}
```

## 🎨 Styling Examples

### CSS Base Styles
```css
.form-field textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  min-height: 5rem;
}

.form-field textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.field-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.25rem;
}

.char-count {
  color: #6b7280;
  font-size: 0.875rem;
}

.char-count.warning {
  color: #f59e0b;
}

.char-count.error {
  color: #ef4444;
}

/* Auto-resize textarea */
.auto-resize-textarea {
  resize: none;
  overflow: hidden;
}
```

### Auto-Resize Textarea (React)
```jsx
const AutoResizeTextarea = ({ field, value, onChange, error }) => {
  const textareaRef = useRef(null);
  
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, []);
  
  useEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);
  
  const handleChange = (e) => {
    onChange(field.id, e.target.value);
    adjustHeight();
  };
  
  return (
    <div className="form-field">
      <label htmlFor={field.id}>{field.label}</label>
      <textarea
        ref={textareaRef}
        id={field.id}
        name={field.id}
        value={value || ''}
        onChange={handleChange}
        className="auto-resize-textarea"
        rows={3}
        placeholder={field.help_text}
      />
    </div>
  );
};
```

## 🔧 Advanced Features

### Character Count with Warnings
```jsx
const TextareaWithCount = ({ field, value, onChange }) => {
  const currentLength = (value || '').length;
  const maxLength = field.max_length || 1000;
  const warningThreshold = maxLength * 0.8; // 80% of max
  
  const getCountClass = () => {
    if (currentLength >= maxLength) return 'char-count error';
    if (currentLength >= warningThreshold) return 'char-count warning';
    return 'char-count';
  };
  
  return (
    <div className="form-field">
      <label htmlFor={field.id}>{field.label}</label>
      <textarea
        id={field.id}
        value={value || ''}
        onChange={(e) => onChange(field.id, e.target.value)}
        maxLength={maxLength}
      />
      <small className={getCountClass()}>
        {currentLength} / {maxLength} characters
        {currentLength >= warningThreshold && ' (approaching limit)'}
      </small>
    </div>
  );
};
```

### Rich Text Editor Integration
```jsx
import ReactQuill from 'react-quill';

const RichTextArea = ({ field, value, onChange }) => {
  const modules = {
    toolbar: [
      ['bold', 'italic', 'underline'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['link'],
      ['clean']
    ],
  };
  
  return (
    <div className="form-field">
      <label>{field.label}</label>
      <ReactQuill
        value={value || ''}
        onChange={(content) => onChange(field.id, content)}
        modules={modules}
        placeholder={field.help_text}
      />
    </div>
  );
};
```

## 🔄 Conditional Logic

Multi-line fields can trigger conditional logic based on content:

**Example API Response:**
```json
{
  "form_fields": [
    {
      "id": "inquiry_type",
      "label": "Inquiry Type",
      "field_type": "dropdown",
      "choices": [["support", "Support"], ["feedback", "Feedback"]]
    },
    {
      "id": "detailed_message",
      "label": "Detailed Message",
      "field_type": "multiline",
      "max_length": 2000,
      "conditional_logic": {
        "action": "show",
        "conditions": [
          {
            "field": "inquiry_type",
            "operator": "equals",
            "value": "feedback"
          }
        ]
      }
    }
  ]
}
```

## 📱 Mobile Optimization

### Mobile-Friendly Textarea
```css
@media (max-width: 768px) {
  .form-field textarea {
    font-size: 16px; /* Prevents zoom on iOS */
    min-height: 4rem;
  }
  
  .field-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
```

## 📝 Form Submission

When submitting, include the textarea content:

```javascript
const formData = {
  "message": "This is a detailed message\nwith multiple lines\nof content.",
  "inquiry_type": "support"
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

Multi-line fields are essential for collecting detailed user input and provide flexible text entry with proper validation and user experience enhancements.


