# Multi-Select Field (Multiple Dropdown)

A dropdown-style field that allows users to select multiple options from a list. Similar to checkboxes but in a more compact dropdown format.

## 🎯 Use Cases

- **Skills Selection**: Programming languages, software tools, technologies
- **Location Selection**: Multiple cities, countries, regions
- **Tag Selection**: Content tags, categories, classifications
- **Feature Selection**: Product features, service options
- **Team Members**: Multiple people, departments, roles
- **Compact Multi-Choice**: When space is limited but multiple selections needed

## 📋 API Response

```json
{
  "id": "programming_languages",
  "label": "Programming Languages",
  "field_type": "multiselect",
  "required": false,
  "help_text": "Select all programming languages you're familiar with",
  "choices": [
    ["javascript", "JavaScript"],
    ["python", "Python"],
    ["java", "Java"],
    ["csharp", "C#"],
    ["php", "PHP"],
    ["go", "Go"],
    ["rust", "Rust"],
    ["typescript", "TypeScript"]
  ],
  "default_value": [],
  "max_selections": 5
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"multiselect"` |
| `choices` | array | Array of [value, label] pairs |
| `default_value` | array | Pre-selected option values |
| `max_selections` | integer | Maximum number of selections allowed |
| All standard properties | - | Required, label, help_text, etc. |

## 🔧 Frontend Implementation

### HTML Example (Native)
```html
<div class="form-field">
  <label for="programming_languages">
    Programming Languages
  </label>
  <select id="programming_languages" name="programming_languages[]" multiple size="6">
    <option value="javascript">JavaScript</option>
    <option value="python">Python</option>
    <option value="java">Java</option>
    <option value="csharp">C#</option>
    <option value="php">PHP</option>
    <option value="go">Go</option>
    <option value="rust">Rust</option>
    <option value="typescript">TypeScript</option>
  </select>
  <small class="help-text">
    Hold Ctrl (Cmd on Mac) to select multiple options
  </small>
</div>
```

### React Example (Custom Component)
```jsx
const MultiSelectField = ({ field, value, onChange, error }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const selectedValues = value || field.default_value || [];
  
  const filteredChoices = field.choices.filter(([_, label]) =>
    label.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const handleOptionToggle = (optionValue) => {
    let newValues;
    if (selectedValues.includes(optionValue)) {
      newValues = selectedValues.filter(val => val !== optionValue);
    } else {
      if (field.max_selections && selectedValues.length >= field.max_selections) {
        return; // Don't allow more selections
      }
      newValues = [...selectedValues, optionValue];
    }
    onChange(field.id, newValues);
  };
  
  const getSelectedLabels = () => {
    return field.choices
      .filter(([value]) => selectedValues.includes(value))
      .map(([_, label]) => label);
  };
  
  return (
    <div className="form-field">
      <label htmlFor={field.id}>
        {field.label}
        {field.required && <span className="required">*</span>}
      </label>
      
      <div className="multiselect-container">
        <div 
          className={`multiselect-trigger ${isOpen ? 'open' : ''}`}
          onClick={() => setIsOpen(!isOpen)}
        >
          <div className="selected-items">
            {selectedValues.length === 0 ? (
              <span className="placeholder">Select options...</span>
            ) : (
              <div className="selected-tags">
                {getSelectedLabels().map((label, index) => (
                  <span key={index} className="selected-tag">
                    {label}
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        const valueToRemove = field.choices.find(([_, l]) => l === label)?.[0];
                        if (valueToRemove) handleOptionToggle(valueToRemove);
                      }}
                      className="remove-tag"
                      aria-label={`Remove ${label}`}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
          <div className="dropdown-arrow">▼</div>
        </div>
        
        {isOpen && (
          <div className="multiselect-dropdown">
            <div className="search-box">
              <input
                type="text"
                placeholder="Search options..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            
            <div className="options-list">
              {filteredChoices.map(([optionValue, optionLabel]) => {
                const isSelected = selectedValues.includes(optionValue);
                const isDisabled = !isSelected && field.max_selections && 
                                  selectedValues.length >= field.max_selections;
                
                return (
                  <div
                    key={optionValue}
                    className={`option ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}`}
                    onClick={() => !isDisabled && handleOptionToggle(optionValue)}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      disabled={isDisabled}
                      readOnly
                    />
                    <span className="option-label">{optionLabel}</span>
                  </div>
                );
              })}
            </div>
            
            {field.max_selections && (
              <div className="selection-info">
                {selectedValues.length} / {field.max_selections} selected
              </div>
            )}
          </div>
        )}
      </div>
      
      {field.help_text && (
        <small className="help-text">{field.help_text}</small>
      )}
      {error && <span className="error">{error}</span>}
    </div>
  );
};
```

## ✅ Validation

### Client-Side Validation
```javascript
const validateMultiSelectField = (field, value) => {
  const errors = [];
  const selectedValues = value || [];
  
  // Required validation
  if (field.required && selectedValues.length === 0) {
    errors.push(`Please select at least one ${field.label.toLowerCase()}`);
  }
  
  // Max selections validation
  if (field.max_selections && selectedValues.length > field.max_selections) {
    errors.push(`Please select no more than ${field.max_selections} options`);
  }
  
  // Min selections validation
  if (field.min_selections && selectedValues.length < field.min_selections) {
    errors.push(`Please select at least ${field.min_selections} options`);
  }
  
  // Valid choices validation
  if (selectedValues.length > 0) {
    const validChoices = field.choices.map(([choiceValue]) => choiceValue);
    const invalidSelections = selectedValues.filter(val => !validChoices.includes(val));
    
    if (invalidSelections.length > 0) {
      errors.push(`Invalid selections detected`);
    }
  }
  
  return errors;
};
```

### Server-Side Validation
The API automatically validates:
- **Selection limits**: Enforces min/max selection rules
- **Valid choices**: All selected values exist in choices
- **Array format**: Ensures proper data format
- **Required fields**: At least one selection if required

## 🎨 Styling Examples

### CSS Base Styles
```css
.multiselect-container {
  position: relative;
}

.multiselect-trigger {
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.5rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 2.5rem;
  background: white;
}

.multiselect-trigger:hover {
  border-color: #9ca3af;
}

.multiselect-trigger.open {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.selected-items {
  flex: 1;
}

.placeholder {
  color: #6b7280;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.selected-tag {
  background: #3b82f6;
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.remove-tag {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}

.dropdown-arrow {
  color: #6b7280;
  transition: transform 0.2s;
}

.multiselect-trigger.open .dropdown-arrow {
  transform: rotate(180deg);
}

.multiselect-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 10;
  max-height: 200px;
  overflow: hidden;
}

.search-box {
  width: 100%;
  padding: 0.5rem;
  border: none;
  border-bottom: 1px solid #e5e7eb;
}

.options-list {
  max-height: 150px;
  overflow-y: auto;
}

.option {
  padding: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.option:hover:not(.disabled) {
  background: #f3f4f6;
}

.option.selected {
  background: #dbeafe;
}

.option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.selection-info {
  padding: 0.5rem;
  border-top: 1px solid #e5e7eb;
  font-size: 0.875rem;
  color: #6b7280;
  text-align: center;
}
```

## 🔄 Advanced Features

### Grouped Options
```jsx
const GroupedMultiSelect = ({ field, value, onChange }) => {
  const groupedChoices = field.choice_groups || [];
  
  return (
    <div className="multiselect-dropdown">
      {groupedChoices.map(group => (
        <div key={group.label} className="option-group">
          <div className="group-header">{group.label}</div>
          {group.choices.map(([optionValue, optionLabel]) => (
            <div
              key={optionValue}
              className={`option ${selectedValues.includes(optionValue) ? 'selected' : ''}`}
              onClick={() => handleOptionToggle(optionValue)}
            >
              <input type="checkbox" checked={selectedValues.includes(optionValue)} readOnly />
              <span>{optionLabel}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};
```

### Async Loading
```jsx
const AsyncMultiSelect = ({ field, value, onChange }) => {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const loadOptions = async (search = '') => {
    setLoading(true);
    try {
      const response = await fetch(`/api/options/${field.option_source}?search=${search}`);
      const data = await response.json();
      setOptions(data.choices);
    } catch (error) {
      console.error('Failed to load options:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadOptions();
  }, []);
  
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchTerm) {
        loadOptions(searchTerm);
      }
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [searchTerm]);
  
  return (
    <div className="multiselect-container">
      {/* Implementation with loading states */}
      {loading && <div className="loading">Loading options...</div>}
      {/* ... rest of component */}
    </div>
  );
};
```

## 📝 Form Submission

Multi-select fields submit arrays of selected values:

```javascript
const formData = {
  "programming_languages": ["javascript", "python", "typescript"],
  "skills": ["react", "node", "docker"],
  "locations": ["new_york", "london"]
};

fetch('/api/form_by_path/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    path: '/profile-form/',
    form_data: formData
  })
});
```

## ⚠️ Best Practices

### DO:
- ✅ Provide search functionality for many options
- ✅ Show selected count and limits clearly
- ✅ Use tags to display selections
- ✅ Allow easy removal of selections
- ✅ Group related options logically

### DON'T:
- ❌ Use for fewer than 4-5 options (use checkboxes)
- ❌ Allow unlimited selections without warning
- ❌ Hide the search functionality
- ❌ Make options too hard to distinguish
- ❌ Forget mobile optimization

Multi-select fields provide a compact way to handle multiple selections with advanced search and filtering capabilities while maintaining a clean user interface.


