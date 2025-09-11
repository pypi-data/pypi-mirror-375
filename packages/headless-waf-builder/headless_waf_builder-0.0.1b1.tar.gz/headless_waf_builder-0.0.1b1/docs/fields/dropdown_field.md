# Dropdown Field (Select)

A select dropdown field that allows users to choose one option from a predefined list of choices.

## 🎯 Use Cases

- **Categories**: Product categories, service types, departments
- **Locations**: Countries, states, cities
- **Preferences**: Size options, color choices, priorities  
- **Status Selection**: Order status, account type, subscription level
- **Any Single Choice**: When users need to pick one option from many

## 📋 API Response

```json
{
  "id": "country",
  "label": "Country",
  "field_type": "dropdown",
  "required": true,
  "help_text": "Select your country",
  "choices": [
    ["us", "United States"],
    ["ca", "Canada"], 
    ["uk", "United Kingdom"],
    ["au", "Australia"]
  ],
  "default_value": "",
  "empty_label": "Choose a country..."
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"dropdown"` |
| `choices` | array | Array of [value, label] pairs |
| `empty_label` | string | Optional placeholder text |
| `default_value` | string | Pre-selected option value |
| All standard properties | - | Required, label, help_text, etc. |

## 🔧 Frontend Implementation

### HTML Example
```html
<div class="form-field">
  <label for="country">
    Country <span class="required">*</span>
  </label>
  <select id="country" name="country" required>
    <option value="">Choose a country...</option>
    <option value="us">United States</option>
    <option value="ca">Canada</option>
    <option value="uk">United Kingdom</option>
    <option value="au">Australia</option>
  </select>
  <small class="help-text">Select your country</small>
</div>
```

### React Example
```jsx
const DropdownField = ({ field, value, onChange, error }) => (
  <div className="form-field">
    <label htmlFor={field.id}>
      {field.label}
      {field.required && <span className="required">*</span>}
    </label>
    <select
      id={field.id}
      name={field.id}
      value={value || field.default_value || ''}
      onChange={(e) => onChange(field.id, e.target.value)}
      required={field.required}
    >
      {field.empty_label && (
        <option value="">{field.empty_label}</option>
      )}
      {field.choices.map(([choiceValue, choiceLabel]) => (
        <option key={choiceValue} value={choiceValue}>
          {choiceLabel}
        </option>
      ))}
    </select>
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
const validateDropdownField = (field, value) => {
  const errors = [];
  
  // Required validation
  if (field.required && (!value || value === '')) {
    errors.push(`${field.label} is required`);
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
- **Required fields**: Returns 422 if no selection made
- **Valid choices**: Ensures selected value exists in choices
- **Data integrity**: Prevents invalid option submissions

**Error Response Example:**
```json
{
  "detail": [
    {
      "field": "country",
      "message": "Select a valid choice. 'invalid' is not one of the available choices."
    }
  ]
}
```

## 🎨 Advanced Styling

### CSS Base Styles
```css
.form-field select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  background-color: white;
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
  appearance: none;
}

.form-field select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-field select:disabled {
  background-color: #f9fafb;
  color: #6b7280;
}
```

### Custom Styled Select (React)
```jsx
const CustomDropdown = ({ field, value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedLabel, setSelectedLabel] = useState('');
  
  useEffect(() => {
    const selected = field.choices.find(([val]) => val === value);
    setSelectedLabel(selected ? selected[1] : field.empty_label || '');
  }, [value, field]);
  
  return (
    <div className="custom-dropdown">
      <button
        type="button"
        className="dropdown-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        {selectedLabel}
        <ChevronDownIcon />
      </button>
      
      {isOpen && (
        <div className="dropdown-menu">
          {field.empty_label && (
            <button
              onClick={() => {
                onChange(field.id, '');
                setIsOpen(false);
              }}
              className="dropdown-item"
            >
              {field.empty_label}
            </button>
          )}
          {field.choices.map(([choiceValue, choiceLabel]) => (
            <button
              key={choiceValue}
              onClick={() => {
                onChange(field.id, choiceValue);
                setIsOpen(false);
              }}
              className={`dropdown-item ${value === choiceValue ? 'selected' : ''}`}
            >
              {choiceLabel}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
```

## 🔄 Conditional Logic

Dropdown fields are excellent for triggering conditional logic:

**Example API Response:**
```json
{
  "form_fields": [
    {
      "id": "account_type",
      "label": "Account Type",
      "field_type": "dropdown",
      "choices": [["personal", "Personal"], ["business", "Business"]],
      "required": true
    },
    {
      "id": "company_name",
      "label": "Company Name", 
      "field_type": "singleline",
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

## 🌐 Dynamic Options

### Loading Options from API
```javascript
const DynamicDropdown = ({ field, value, onChange }) => {
  const [options, setOptions] = useState(field.choices || []);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Load dynamic options if needed
    if (field.dynamic_source) {
      setLoading(true);
      fetch(`/api/options/${field.dynamic_source}`)
        .then(r => r.json())
        .then(data => setOptions(data.choices))
        .finally(() => setLoading(false));
    }
  }, [field.dynamic_source]);
  
  return (
    <select disabled={loading} /* ... other props */>
      {loading ? (
        <option>Loading...</option>
      ) : (
        options.map(([val, label]) => (
          <option key={val} value={val}>{label}</option>
        ))
      )}
    </select>
  );
};
```

## 📝 Form Submission

When submitting, include the selected value:

```javascript
const formData = {
  "country": "us",
  "account_type": "business"
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

Dropdown fields provide structured data collection and are essential for forms requiring categorized user input with clear, predefined options.


