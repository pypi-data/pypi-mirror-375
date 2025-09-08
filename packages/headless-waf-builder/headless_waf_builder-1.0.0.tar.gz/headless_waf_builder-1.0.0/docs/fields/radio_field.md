# Radio Field (Radio Button Group)

A radio button group field that allows users to select exactly one option from a list of mutually exclusive choices.

## 🎯 Use Cases

- **Single Selection**: Choose one option where only one answer is valid
- **Yes/No Questions**: Binary choices with custom labels
- **Priority Levels**: High, Medium, Low priority selection
- **Payment Methods**: Credit card, PayPal, bank transfer
- **Size Selection**: Small, Medium, Large, XL
- **Rating Scales**: Poor, Fair, Good, Excellent

## 📋 API Response

```json
{
  "id": "contact_method",
  "label": "Preferred Contact Method",
  "field_type": "radio",
  "required": true,
  "help_text": "How would you like us to contact you?",
  "choices": [
    ["email", "Email"],
    ["phone", "Phone"],
    ["sms", "Text Message"],
    ["mail", "Postal Mail"]
  ],
  "default_value": "email",
  "display_side_by_side": false
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"radio"` |
| `choices` | array | Array of [value, label] pairs |
| `default_value` | string | Pre-selected option value |
| `display_side_by_side` | boolean | Layout options horizontally |
| All standard properties | - | Required, label, help_text, etc. |

## 🔧 Frontend Implementation

### HTML Example
```html
<div class="form-field">
  <fieldset>
    <legend>
      Preferred Contact Method <span class="required">*</span>
    </legend>
    <div class="radio-group">
      <div class="radio-option">
        <input type="radio" id="contact_email" name="contact_method" value="email" checked required>
        <label for="contact_email">Email</label>
      </div>
      <div class="radio-option">
        <input type="radio" id="contact_phone" name="contact_method" value="phone" required>
        <label for="contact_phone">Phone</label>
      </div>
      <div class="radio-option">
        <input type="radio" id="contact_sms" name="contact_method" value="sms" required>
        <label for="contact_sms">Text Message</label>
      </div>
      <div class="radio-option">
        <input type="radio" id="contact_mail" name="contact_method" value="mail" required>
        <label for="contact_mail">Postal Mail</label>
      </div>
    </div>
    <small class="help-text">How would you like us to contact you?</small>
  </fieldset>
</div>
```

### React Example
```jsx
const RadioField = ({ field, value, onChange, error }) => (
  <div className="form-field">
    <fieldset>
      <legend>
        {field.label}
        {field.required && <span className="required">*</span>}
      </legend>
      <div className={`radio-group ${field.display_side_by_side ? 'side-by-side' : ''}`}>
        {field.choices.map(([choiceValue, choiceLabel]) => (
          <div key={choiceValue} className="radio-option">
            <input
              type="radio"
              id={`${field.id}_${choiceValue}`}
              name={field.id}
              value={choiceValue}
              checked={value === choiceValue || (!value && field.default_value === choiceValue)}
              onChange={(e) => onChange(field.id, e.target.value)}
              required={field.required}
            />
            <label htmlFor={`${field.id}_${choiceValue}`}>
              {choiceLabel}
            </label>
          </div>
        ))}
      </div>
      {field.help_text && (
        <small className="help-text">{field.help_text}</small>
      )}
      {error && <span className="error">{error}</span>}
    </fieldset>
  </div>
);
```

## ✅ Validation

### Client-Side Validation
```javascript
const validateRadioField = (field, value) => {
  const errors = [];
  
  // Required validation
  if (field.required && (!value || value === '')) {
    errors.push(`Please select a ${field.label.toLowerCase()}`);
    return errors;
  }
  
  // Valid choice validation
  if (value) {
    const validChoices = field.choices.map(([choiceValue]) => choiceValue);
    if (!validChoices.includes(value)) {
      errors.push(`Please select a valid ${field.label.toLowerCase()}`);
    }
  }
  
  return errors;
};
```

### Server-Side Validation
The API automatically validates:
- **Required selection**: Returns 422 if no option selected
- **Valid choices**: Ensures selected value exists in choices
- **Single selection**: Prevents multiple values

**Error Response Example:**
```json
{
  "detail": [
    {
      "field": "contact_method",
      "message": "This field is required."
    }
  ]
}
```

## 🎨 Styling Examples

### CSS Base Styles
```css
.form-field fieldset {
  border: none;
  padding: 0;
  margin: 0;
}

.form-field legend {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.radio-group.side-by-side {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 1rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.radio-option input[type="radio"] {
  margin: 0;
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.radio-option label {
  cursor: pointer;
  user-select: none;
  line-height: 1.25rem;
}

/* Custom radio styling */
.custom-radio {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.custom-radio input {
  opacity: 0;
  position: absolute;
}

.custom-radio .radio-indicator {
  width: 1rem;
  height: 1rem;
  border: 2px solid #d1d5db;
  border-radius: 50%;
  background: white;
  position: relative;
  flex-shrink: 0;
}

.custom-radio input:checked + .radio-indicator {
  border-color: #3b82f6;
  background: white;
}

.custom-radio input:checked + .radio-indicator::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0.5rem;
  height: 0.5rem;
  background: #3b82f6;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.custom-radio:hover .radio-indicator {
  border-color: #9ca3af;
}

.custom-radio input:focus + .radio-indicator {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
```

### Custom Styled Radio Group (React)
```jsx
const CustomRadioGroup = ({ field, value, onChange, error }) => (
  <div className="form-field">
    <fieldset>
      <legend>{field.label}</legend>
      <div className={`radio-group ${field.display_side_by_side ? 'side-by-side' : ''}`}>
        {field.choices.map(([choiceValue, choiceLabel]) => (
          <label key={choiceValue} className="custom-radio">
            <input
              type="radio"
              name={field.id}
              value={choiceValue}
              checked={value === choiceValue}
              onChange={(e) => onChange(field.id, e.target.value)}
              required={field.required}
            />
            <span className="radio-indicator"></span>
            <span className="radio-label">{choiceLabel}</span>
          </label>
        ))}
      </div>
    </fieldset>
  </div>
);
```

## 🔄 Conditional Logic

Radio fields are excellent triggers for conditional logic:

**Example API Response:**
```json
{
  "form_fields": [
    {
      "id": "account_type",
      "label": "Account Type",
      "field_type": "radio",
      "choices": [
        ["personal", "Personal Account"],
        ["business", "Business Account"]
      ],
      "required": true
    },
    {
      "id": "company_details",
      "label": "Company Details",
      "field_type": "multiline",
      "conditional_logic": {
        "action": "show",
        "conditions": [
          {
            "field": "account_type",
            "operator": "equals",
            "value": "business"
          }
        ]
      }
    }
  ]
}
```

### Multiple Conditions Example
```json
{
  "id": "shipping_options",
  "label": "Shipping Options",
  "field_type": "radio",
  "conditional_logic": {
    "action": "show",
    "conditions": [
      {
        "field": "account_type",
        "operator": "equals",
        "value": "business"
      },
      {
        "field": "order_total",
        "operator": "greater_than",
        "value": 100
      }
    ]
  }
}
```

## 🎨 Advanced Features

### Radio Cards (Enhanced Visual Style)
```jsx
const RadioCards = ({ field, value, onChange }) => (
  <div className="form-field">
    <legend>{field.label}</legend>
    <div className="radio-cards">
      {field.choices.map(([choiceValue, choiceLabel, description]) => (
        <label 
          key={choiceValue} 
          className={`radio-card ${value === choiceValue ? 'selected' : ''}`}
        >
          <input
            type="radio"
            name={field.id}
            value={choiceValue}
            checked={value === choiceValue}
            onChange={(e) => onChange(field.id, e.target.value)}
          />
          <div className="card-content">
            <h4 className="card-title">{choiceLabel}</h4>
            {description && (
              <p className="card-description">{description}</p>
            )}
          </div>
          <div className="card-indicator">
            {value === choiceValue && <CheckIcon />}
          </div>
        </label>
      ))}
    </div>
  </div>
);
```

### Radio with Images
```jsx
const ImageRadioGroup = ({ field, value, onChange }) => (
  <div className="form-field">
    <legend>{field.label}</legend>
    <div className="image-radio-group">
      {field.choices.map(([choiceValue, choiceLabel, imageUrl]) => (
        <label key={choiceValue} className="image-radio-option">
          <input
            type="radio"
            name={field.id}
            value={choiceValue}
            checked={value === choiceValue}
            onChange={(e) => onChange(field.id, e.target.value)}
          />
          <div className="image-container">
            <img src={imageUrl} alt={choiceLabel} />
            <span className="image-label">{choiceLabel}</span>
          </div>
        </label>
      ))}
    </div>
  </div>
);
```

## 📝 Form Submission

When submitting, include the selected radio value:

```javascript
const formData = {
  "contact_method": "email",
  "account_type": "business",
  "priority_level": "high"
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

Radio fields provide clear single-choice selection with excellent conditional logic capabilities, making them essential for forms requiring mutually exclusive options with strong visual hierarchy.


