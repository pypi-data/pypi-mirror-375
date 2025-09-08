# Checkboxes Field (Multiple Selection)

A checkbox group field that allows users to select multiple options from a list of choices. Each option can be independently selected or deselected.

## 🎯 Use Cases

- **Multiple Interests**: Hobbies, skills, services of interest
- **Feature Selection**: Product features, service add-ons, preferences
- **Multi-Category**: Multiple tags, categories, classifications
- **Permissions**: Access levels, feature permissions, capabilities
- **Preferences**: Communication preferences, notification settings
- **Survey Questions**: "Select all that apply" type questions

## 📋 API Response

```json
{
  "id": "interests",
  "label": "Areas of Interest",
  "field_type": "checkboxes",
  "required": false,
  "help_text": "Select all areas that interest you",
  "choices": [
    ["web_design", "Web Design"],
    ["mobile_apps", "Mobile Applications"],
    ["data_science", "Data Science"],
    ["cybersecurity", "Cybersecurity"],
    ["ai_ml", "AI & Machine Learning"]
  ],
  "default_value": [],
  "display_side_by_side": false
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"checkboxes"` |
| `choices` | array | Array of [value, label] pairs |
| `default_value` | array | Pre-selected option values |
| `display_side_by_side` | boolean | Layout options horizontally |
| All standard properties | - | Required, label, help_text, etc. |

## 🔧 Frontend Implementation

### HTML Example
```html
<div class="form-field">
  <fieldset>
    <legend>Areas of Interest</legend>
    <div class="checkboxes-group">
      <div class="checkbox-option">
        <input type="checkbox" id="interests_web_design" name="interests[]" value="web_design">
        <label for="interests_web_design">Web Design</label>
      </div>
      <div class="checkbox-option">
        <input type="checkbox" id="interests_mobile_apps" name="interests[]" value="mobile_apps">
        <label for="interests_mobile_apps">Mobile Applications</label>
      </div>
      <div class="checkbox-option">
        <input type="checkbox" id="interests_data_science" name="interests[]" value="data_science">
        <label for="interests_data_science">Data Science</label>
      </div>
      <div class="checkbox-option">
        <input type="checkbox" id="interests_cybersecurity" name="interests[]" value="cybersecurity">
        <label for="interests_cybersecurity">Cybersecurity</label>
      </div>
      <div class="checkbox-option">
        <input type="checkbox" id="interests_ai_ml" name="interests[]" value="ai_ml">
        <label for="interests_ai_ml">AI & Machine Learning</label>
      </div>
    </div>
    <small class="help-text">Select all areas that interest you</small>
  </fieldset>
</div>
```

### React Example
```jsx
const CheckboxesField = ({ field, value, onChange, error }) => {
  const selectedValues = value || field.default_value || [];
  
  const handleCheckboxChange = (optionValue, isChecked) => {
    let newValues;
    if (isChecked) {
      newValues = [...selectedValues, optionValue];
    } else {
      newValues = selectedValues.filter(val => val !== optionValue);
    }
    onChange(field.id, newValues);
  };
  
  return (
    <div className="form-field">
      <fieldset>
        <legend>
          {field.label}
          {field.required && <span className="required">*</span>}
        </legend>
        <div className={`checkboxes-group ${field.display_side_by_side ? 'side-by-side' : ''}`}>
          {field.choices.map(([choiceValue, choiceLabel]) => (
            <div key={choiceValue} className="checkbox-option">
              <input
                type="checkbox"
                id={`${field.id}_${choiceValue}`}
                name={`${field.id}[]`}
                value={choiceValue}
                checked={selectedValues.includes(choiceValue)}
                onChange={(e) => handleCheckboxChange(choiceValue, e.target.checked)}
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
};
```

## ✅ Validation

### Client-Side Validation
```javascript
const validateCheckboxesField = (field, value) => {
  const errors = [];
  const selectedValues = value || [];
  
  // Required validation (at least one must be selected)
  if (field.required && selectedValues.length === 0) {
    errors.push(`Please select at least one ${field.label.toLowerCase()}`);
  }
  
  // Valid choices validation
  if (selectedValues.length > 0) {
    const validChoices = field.choices.map(([choiceValue]) => choiceValue);
    const invalidSelections = selectedValues.filter(val => !validChoices.includes(val));
    
    if (invalidSelections.length > 0) {
      errors.push(`Invalid selections: ${invalidSelections.join(', ')}`);
    }
  }
  
  // Maximum selections (if configured)
  if (field.max_selections && selectedValues.length > field.max_selections) {
    errors.push(`Please select no more than ${field.max_selections} options`);
  }
  
  // Minimum selections (if configured)
  if (field.min_selections && selectedValues.length < field.min_selections) {
    errors.push(`Please select at least ${field.min_selections} options`);
  }
  
  return errors;
};
```

### Server-Side Validation
The API automatically validates:
- **Required selections**: At least one option if required
- **Valid choices**: All selected values exist in choices
- **Array format**: Ensures data is submitted as array
- **Data integrity**: Prevents malicious option injection

**Error Response Example:**
```json
{
  "detail": [
    {
      "field": "interests",
      "message": "This field is required."
    }
  ]
}
```

## 🎨 Styling Examples

### CSS Base Styles
```css
.checkboxes-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkboxes-group.side-by-side {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 1rem;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-option input[type="checkbox"] {
  margin: 0;
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.checkbox-option label {
  cursor: pointer;
  user-select: none;
  line-height: 1.25rem;
}

/* Grid layout for many options */
.checkboxes-group.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

/* Card-style checkboxes */
.checkbox-card {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.checkbox-card:hover {
  border-color: #9ca3af;
  background-color: #f9fafb;
}

.checkbox-card.selected {
  border-color: #3b82f6;
  background-color: #dbeafe;
}
```

### Advanced Checkboxes with Icons (React)
```jsx
const IconCheckboxesField = ({ field, value, onChange }) => {
  const selectedValues = value || [];
  
  const choiceIcons = {
    'web_design': '🎨',
    'mobile_apps': '📱',
    'data_science': '📊',
    'cybersecurity': '🔒',
    'ai_ml': '🤖'
  };
  
  return (
    <div className="form-field">
      <legend>{field.label}</legend>
      <div className="icon-checkboxes-grid">
        {field.choices.map(([choiceValue, choiceLabel]) => {
          const isSelected = selectedValues.includes(choiceValue);
          return (
            <label 
              key={choiceValue} 
              className={`checkbox-card ${isSelected ? 'selected' : ''}`}
            >
              <input
                type="checkbox"
                value={choiceValue}
                checked={isSelected}
                onChange={(e) => {
                  const newValues = e.target.checked
                    ? [...selectedValues, choiceValue]
                    : selectedValues.filter(v => v !== choiceValue);
                  onChange(field.id, newValues);
                }}
                style={{ display: 'none' }}
              />
              <div className="card-content">
                <div className="card-icon">
                  {choiceIcons[choiceValue] || '✓'}
                </div>
                <div className="card-label">{choiceLabel}</div>
              </div>
            </label>
          );
        })}
      </div>
    </div>
  );
};
```

## 🔄 Advanced Features

### Select All / Deselect All
```jsx
const CheckboxesWithSelectAll = ({ field, value, onChange }) => {
  const selectedValues = value || [];
  const allValues = field.choices.map(([choiceValue]) => choiceValue);
  const isAllSelected = allValues.length > 0 && allValues.every(val => selectedValues.includes(val));
  const isNoneSelected = selectedValues.length === 0;
  
  const handleSelectAll = () => {
    onChange(field.id, isAllSelected ? [] : allValues);
  };
  
  return (
    <div className="form-field">
      <fieldset>
        <legend>{field.label}</legend>
        
        <div className="select-all-controls">
          <label className="select-all-option">
            <input
              type="checkbox"
              checked={isAllSelected}
              onChange={handleSelectAll}
              indeterminate={!isAllSelected && !isNoneSelected}
            />
            <span>Select All</span>
          </label>
        </div>
        
        <div className="checkboxes-group">
          {field.choices.map(([choiceValue, choiceLabel]) => (
            <div key={choiceValue} className="checkbox-option">
              <input
                type="checkbox"
                id={`${field.id}_${choiceValue}`}
                checked={selectedValues.includes(choiceValue)}
                onChange={(e) => {
                  const newValues = e.target.checked
                    ? [...selectedValues, choiceValue]
                    : selectedValues.filter(v => v !== choiceValue);
                  onChange(field.id, newValues);
                }}
              />
              <label htmlFor={`${field.id}_${choiceValue}`}>
                {choiceLabel}
              </label>
            </div>
          ))}
        </div>
      </fieldset>
    </div>
  );
};
```

### Searchable Checkboxes
```jsx
const SearchableCheckboxes = ({ field, value, onChange }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const selectedValues = value || [];
  
  const filteredChoices = field.choices.filter(([_, label]) =>
    label.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  return (
    <div className="form-field">
      <legend>{field.label}</legend>
      
      <div className="search-input">
        <input
          type="text"
          placeholder="Search options..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      <div className="checkboxes-group">
        {filteredChoices.map(([choiceValue, choiceLabel]) => (
          <div key={choiceValue} className="checkbox-option">
            <input
              type="checkbox"
              id={`${field.id}_${choiceValue}`}
              checked={selectedValues.includes(choiceValue)}
              onChange={(e) => {
                const newValues = e.target.checked
                  ? [...selectedValues, choiceValue]
                  : selectedValues.filter(v => v !== choiceValue);
                onChange(field.id, newValues);
              }}
            />
            <label htmlFor={`${field.id}_${choiceValue}`}>
              {choiceLabel}
            </label>
          </div>
        ))}
      </div>
      
      {selectedValues.length > 0 && (
        <div className="selected-count">
          {selectedValues.length} selected
        </div>
      )}
    </div>
  );
};
```

## 🔄 Conditional Logic

Checkboxes fields can trigger conditional logic based on selections:

**Example API Response:**
```json
{
  "form_fields": [
    {
      "id": "services",
      "label": "Services Interested In",
      "field_type": "checkboxes",
      "choices": [
        ["web_dev", "Web Development"],
        ["mobile_dev", "Mobile Development"],
        ["consulting", "Consulting"]
      ]
    },
    {
      "id": "web_tech_preferences",
      "label": "Web Technology Preferences",
      "field_type": "checkboxes",
      "choices": [
        ["react", "React"],
        ["vue", "Vue.js"],
        ["angular", "Angular"]
      ],
      "conditional_logic": {
        "action": "show",
        "conditions": [
          {
            "field": "services",
            "operator": "contains",
            "value": "web_dev"
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
    const fieldValue = formData[condition.field] || [];
    
    switch (condition.operator) {
      case 'contains':
        return Array.isArray(fieldValue) && fieldValue.includes(condition.value);
      case 'not_contains':
        return !Array.isArray(fieldValue) || !fieldValue.includes(condition.value);
      case 'has_any':
        return Array.isArray(fieldValue) && fieldValue.length > 0;
      case 'has_none':
        return !Array.isArray(fieldValue) || fieldValue.length === 0;
      default:
        return true;
    }
  });
};
```

## 📝 Form Submission

When submitting, include the selected values as an array:

```javascript
const formData = {
  "interests": ["web_design", "ai_ml", "cybersecurity"],
  "services": ["web_dev", "consulting"],
  "preferences": []
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
- ✅ Group related options logically
- ✅ Use clear, descriptive labels
- ✅ Provide "Select All" for many options
- ✅ Show selection count for clarity
- ✅ Consider search for 10+ options

### DON'T:
- ❌ Use for mutually exclusive choices (use radio instead)
- ❌ Overwhelm with too many options
- ❌ Make all options required if not necessary
- ❌ Use unclear or ambiguous labels

Checkboxes fields provide flexible multi-selection capabilities with robust validation and user experience enhancements for collecting multiple related preferences or choices.


