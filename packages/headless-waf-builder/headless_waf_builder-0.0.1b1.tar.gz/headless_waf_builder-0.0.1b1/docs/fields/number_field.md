# Number Field

A numeric input field for collecting integer and decimal numbers with built-in validation and formatting.

## 🎯 Use Cases

- **Quantities**: Product quantities, guest counts, item numbers
- **Measurements**: Height, weight, distance, dimensions
- **Financial**: Prices, budgets, salaries (without currency symbols)
- **Ratings**: Numeric ratings, scores, percentages
- **Age/Years**: Age input, years of experience
- **IDs**: Numeric identifiers, account numbers

## 📋 API Response

```json
{
  "id": "quantity",
  "label": "Quantity",
  "field_type": "number",
  "required": true,
  "help_text": "Enter the number of items",
  "choices": null,
  "default_value": 1,
  "max_length": null,
  "min_value": 1,
  "max_value": 100,
  "step": 1
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"number"` |
| `min_value` | number | Minimum allowed value |
| `max_value` | number | Maximum allowed value |
| `step` | number | Step increment (1 for integers, 0.01 for decimals) |
| `default_value` | number | Pre-filled numeric value |
| All standard properties | - | Required, label, help_text, etc. |

## 🔧 Frontend Implementation

### HTML Example
```html
<div class="form-field">
  <label for="quantity">
    Quantity <span class="required">*</span>
  </label>
  <input 
    type="number" 
    id="quantity" 
    name="quantity"
    min="1"
    max="100"
    step="1"
    value="1"
    placeholder="Enter the number of items"
    required
  />
  <small class="help-text">Enter the number of items</small>
</div>
```

### React Example
```jsx
const NumberField = ({ field, value, onChange, error }) => (
  <div className="form-field">
    <label htmlFor={field.id}>
      {field.label}
      {field.required && <span className="required">*</span>}
    </label>
    <input
      type="number"
      id={field.id}
      name={field.id}
      value={value !== undefined ? value : (field.default_value || '')}
      onChange={(e) => {
        const numValue = e.target.value === '' ? '' : Number(e.target.value);
        onChange(field.id, numValue);
      }}
      min={field.min_value}
      max={field.max_value}
      step={field.step || 1}
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
const validateNumberField = (field, value) => {
  const errors = [];
  
  // Required validation
  if (field.required && (value === undefined || value === null || value === '')) {
    errors.push(`${field.label} is required`);
    return errors;
  }
  
  if (value !== undefined && value !== null && value !== '') {
    const numValue = Number(value);
    
    // Valid number check
    if (isNaN(numValue)) {
      errors.push(`${field.label} must be a valid number`);
      return errors;
    }
    
    // Min value validation
    if (field.min_value !== undefined && numValue < field.min_value) {
      errors.push(`${field.label} must be at least ${field.min_value}`);
    }
    
    // Max value validation
    if (field.max_value !== undefined && numValue > field.max_value) {
      errors.push(`${field.label} must be no more than ${field.max_value}`);
    }
    
    // Step validation
    if (field.step && field.min_value !== undefined) {
      const remainder = (numValue - (field.min_value || 0)) % field.step;
      if (Math.abs(remainder) > 0.0001) { // Handle floating point precision
        errors.push(`${field.label} must be in increments of ${field.step}`);
      }
    }
  }
  
  return errors;
};
```

### Server-Side Validation
The API automatically validates:
- **Numeric format**: Ensures value is a valid number
- **Range validation**: Enforces min/max values
- **Step validation**: Validates increment rules
- **Required fields**: Returns 422 if missing

**Error Response Example:**
```json
{
  "detail": [
    {
      "field": "quantity",
      "message": "Ensure this value is greater than or equal to 1."
    }
  ]
}
```

## 🎨 Advanced Styling

### CSS Base Styles
```css
.form-field input[type="number"] {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  text-align: left;
}

.form-field input[type="number"]:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Hide spinner arrows (optional) */
.form-field input[type="number"]::-webkit-outer-spin-button,
.form-field input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-field input[type="number"] {
  -moz-appearance: textfield;
}

/* Custom number input with controls */
.number-input-wrapper {
  display: flex;
  align-items: center;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  overflow: hidden;
}

.number-input-wrapper input {
  border: none;
  padding: 0.5rem;
  flex: 1;
  text-align: center;
}

.number-input-button {
  background: #f9fafb;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  user-select: none;
}

.number-input-button:hover {
  background: #f3f4f6;
}

.number-input-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Custom Number Input with Controls (React)
```jsx
const NumberInputWithControls = ({ field, value, onChange, error }) => {
  const numValue = value !== undefined ? Number(value) : (field.default_value || 0);
  const step = field.step || 1;
  
  const increment = () => {
    const newValue = numValue + step;
    if (!field.max_value || newValue <= field.max_value) {
      onChange(field.id, newValue);
    }
  };
  
  const decrement = () => {
    const newValue = numValue - step;
    if (!field.min_value || newValue >= field.min_value) {
      onChange(field.id, newValue);
    }
  };
  
  const canIncrement = !field.max_value || numValue < field.max_value;
  const canDecrement = !field.min_value || numValue > field.min_value;
  
  return (
    <div className="form-field">
      <label htmlFor={field.id}>{field.label}</label>
      <div className="number-input-wrapper">
        <button
          type="button"
          className="number-input-button"
          onClick={decrement}
          disabled={!canDecrement}
          aria-label="Decrease"
        >
          −
        </button>
        <input
          type="number"
          id={field.id}
          name={field.id}
          value={numValue}
          onChange={(e) => onChange(field.id, Number(e.target.value))}
          min={field.min_value}
          max={field.max_value}
          step={step}
        />
        <button
          type="button"
          className="number-input-button"
          onClick={increment}
          disabled={!canIncrement}
          aria-label="Increase"
        >
          +
        </button>
      </div>
      {error && <span className="error">{error}</span>}
    </div>
  );
};
```

## 🔢 Special Number Types

### Currency Input (Display Only)
```jsx
const CurrencyField = ({ field, value, onChange }) => {
  const [displayValue, setDisplayValue] = useState('');
  
  useEffect(() => {
    if (value) {
      setDisplayValue(new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value));
    }
  }, [value]);
  
  const handleChange = (e) => {
    const cleaned = e.target.value.replace(/[^0-9.]/g, '');
    const numValue = parseFloat(cleaned) || 0;
    onChange(field.id, numValue);
  };
  
  return (
    <div className="form-field">
      <label htmlFor={field.id}>{field.label}</label>
      <div className="currency-input">
        <span className="currency-symbol">$</span>
        <input
          type="number"
          id={field.id}
          step="0.01"
          min="0"
          value={value || ''}
          onChange={(e) => onChange(field.id, Number(e.target.value))}
          placeholder="0.00"
        />
      </div>
    </div>
  );
};
```

### Percentage Input
```jsx
const PercentageField = ({ field, value, onChange }) => (
  <div className="form-field">
    <label htmlFor={field.id}>{field.label}</label>
    <div className="percentage-input">
      <input
        type="number"
        id={field.id}
        value={value || ''}
        onChange={(e) => onChange(field.id, Number(e.target.value))}
        min={0}
        max={100}
        step={0.1}
      />
      <span className="percentage-symbol">%</span>
    </div>
  </div>
);
```

## 🔄 Conditional Logic

Number fields can trigger conditional logic based on value ranges:

**Example API Response:**
```json
{
  "form_fields": [
    {
      "id": "age",
      "label": "Age",
      "field_type": "number",
      "min_value": 0,
      "max_value": 120,
      "required": true
    },
    {
      "id": "guardian_consent",
      "label": "Guardian Consent",
      "field_type": "checkbox",
      "conditional_logic": {
        "action": "show",
        "conditions": [
          {
            "field": "age",
            "operator": "less_than",
            "value": 18
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
    const fieldValue = Number(formData[condition.field]);
    const conditionValue = Number(condition.value);
    
    switch (condition.operator) {
      case 'equals':
        return fieldValue === conditionValue;
      case 'greater_than':
        return fieldValue > conditionValue;
      case 'less_than':
        return fieldValue < conditionValue;
      case 'greater_than_equal':
        return fieldValue >= conditionValue;
      case 'less_than_equal':
        return fieldValue <= conditionValue;
      default:
        return true;
    }
  });
};
```

## 📝 Form Submission

When submitting, ensure numbers are properly formatted:

```javascript
const formData = {
  "quantity": 5,
  "price": 29.99,
  "age": 25,
  "percentage": 85.5
};

fetch('/api/form_by_path/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    path: '/order-form/',
    form_data: formData
  })
});
```

Number fields provide robust numeric input with validation, formatting, and accessibility features essential for data collection requiring precise numeric values.


