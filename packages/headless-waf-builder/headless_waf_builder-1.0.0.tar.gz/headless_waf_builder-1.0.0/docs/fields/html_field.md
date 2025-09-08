# HTML Field (Display Content)

A display-only field for showing formatted HTML content, instructions, or rich text within forms without collecting user input.

## 🎯 Use Cases

- **Instructions**: Form filling guidance, step-by-step directions
- **Legal Text**: Terms of service, privacy notices, disclaimers
- **Contextual Information**: Explanatory content, help sections
- **Formatting**: Visual separators, section headers, dividers
- **Rich Content**: Links, lists, formatted text, images
- **Dynamic Content**: Conditional messaging, personalized text

## 📋 API Response

```json
{
  "id": "privacy_notice",
  "label": "Privacy Notice",
  "field_type": "html",
  "required": false,
  "help_text": "",
  "choices": null,
  "default_value": "",
  "html_content": "<div class='notice'><h3>Privacy Notice</h3><p>We protect your personal information. Read our <a href='/privacy' target='_blank'>privacy policy</a> for details.</p></div>"
}
```

## ⚙️ Configuration & Properties

| Property | Type | Description |
|----------|------|-------------|
| `field_type` | string | Always `"html"` |
| `html_content` | string | The HTML content to display |
| `label` | string | For admin purposes (not displayed) |
| All standard properties | - | help_text, etc. (mainly for admin) |

**Note**: HTML fields don't collect input and are typically not required.

## 🔧 Frontend Implementation

### React Example
```jsx
const HTMLField = ({ field }) => (
  <div className="html-field" id={field.id}>
    <div 
      dangerouslySetInnerHTML={{ __html: field.html_content }}
      className="html-content"
    />
  </div>
);

// Safer implementation with sanitization
import DOMPurify from 'dompurify';

const SafeHTMLField = ({ field }) => {
  const sanitizedHTML = DOMPurify.sanitize(field.html_content);
  
  return (
    <div className="html-field" id={field.id}>
      <div 
        dangerouslySetInnerHTML={{ __html: sanitizedHTML }}
        className="html-content"
      />
    </div>
  );
};
```

### HTML Example (Server-Rendered)
```html
<div class="html-field" id="privacy_notice">
  <div class="html-content">
    <div class='notice'>
      <h3>Privacy Notice</h3>
      <p>We protect your personal information. Read our <a href='/privacy' target='_blank'>privacy policy</a> for details.</p>
    </div>
  </div>
</div>
```

## 🔒 Security Implementation

### HTML Sanitization
```javascript
import DOMPurify from 'dompurify';

const sanitizeHTML = (html) => {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'div', 'span', 'p', 'br', 'strong', 'em', 'u', 'a', 
      'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'blockquote', 'code', 'pre'
    ],
    ALLOWED_ATTR: ['href', 'target', 'class', 'id'],
    ALLOW_DATA_ATTR: false
  });
};

const SecureHTMLField = ({ field }) => {
  const sanitizedContent = sanitizeHTML(field.html_content);
  
  return (
    <div className="html-field">
      <div dangerouslySetInnerHTML={{ __html: sanitizedContent }} />
    </div>
  );
};
```

### Content Security Policy
```javascript
// Configure CSP headers for HTML content
const cspConfig = {
  'default-src': "'self'",
  'img-src': "'self' data: https:",
  'style-src': "'self' 'unsafe-inline'",
  'script-src': "'self'", // No inline scripts
  'object-src': "'none'"
};
```

## 🎨 Styling Examples

### CSS Base Styles
```css
.html-field {
  margin-bottom: 1.5rem;
}

.html-content {
  line-height: 1.6;
  color: #374151;
}

.html-content h1,
.html-content h2,
.html-content h3,
.html-content h4,
.html-content h5,
.html-content h6 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.html-content p {
  margin-bottom: 1rem;
}

.html-content a {
  color: #3b82f6;
  text-decoration: underline;
}

.html-content a:hover {
  color: #1d4ed8;
}

.html-content ul,
.html-content ol {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.html-content blockquote {
  border-left: 4px solid #e5e7eb;
  padding-left: 1rem;
  margin: 1rem 0;
  font-style: italic;
  color: #6b7280;
}

.html-content code {
  background-color: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: monospace;
  font-size: 0.875em;
}

.html-content pre {
  background-color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1rem 0;
}

/* Special styling for notices */
.html-content .notice {
  background-color: #dbeafe;
  border: 1px solid #93c5fd;
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
}

.html-content .warning {
  background-color: #fef3c7;
  border: 1px solid #fbbf24;
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
}

.html-content .success {
  background-color: #d1fae5;
  border: 1px solid #6ee7b7;
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
}
```

## 🔄 Dynamic HTML Content

### Conditional HTML Content
```jsx
const ConditionalHTMLField = ({ field, formData }) => {
  const [htmlContent, setHtmlContent] = useState(field.html_content);
  
  useEffect(() => {
    // Update content based on form data
    let content = field.html_content;
    
    // Replace placeholders with form data
    Object.keys(formData).forEach(key => {
      const placeholder = `{{${key}}}`;
      content = content.replace(new RegExp(placeholder, 'g'), formData[key] || '');
    });
    
    setHtmlContent(content);
  }, [field.html_content, formData]);
  
  return (
    <div className="html-field">
      <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(htmlContent) }} />
    </div>
  );
};
```

### Template-Based HTML Fields
```jsx
const TemplateHTMLField = ({ field, context }) => {
  const renderTemplate = (template, data) => {
    return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return data[key] || match;
    });
  };
  
  const renderedContent = renderTemplate(field.html_content, {
    userName: context.user?.name || 'User',
    companyName: context.company?.name || 'Your Company',
    currentDate: new Date().toLocaleDateString(),
    formCount: context.stats?.formCount || 0
  });
  
  return (
    <div className="html-field">
      <div dangerouslySetInnerHTML={{ 
        __html: DOMPurify.sanitize(renderedContent) 
      }} />
    </div>
  );
};
```

## 🔗 HTML Field with Links

### Link Handling
```jsx
const HTMLFieldWithLinkTracking = ({ field }) => {
  const handleClick = (e) => {
    if (e.target.tagName === 'A') {
      // Track link clicks
      const href = e.target.href;
      const text = e.target.textContent;
      
      // Analytics tracking
      trackEvent('html_field_link_click', {
        field_id: field.id,
        link_url: href,
        link_text: text
      });
      
      // Open external links in new tab
      if (href.startsWith('http') && !href.includes(window.location.hostname)) {
        e.preventDefault();
        window.open(href, '_blank', 'noopener,noreferrer');
      }
    }
  };
  
  return (
    <div className="html-field" onClick={handleClick}>
      <div dangerouslySetInnerHTML={{ 
        __html: DOMPurify.sanitize(field.html_content) 
      }} />
    </div>
  );
};
```

## 📝 Form Integration

HTML fields don't participate in form submission but enhance the user experience:

```jsx
const FormWithHTMLFields = ({ formSchema, onSubmit }) => {
  const [formData, setFormData] = useState({});
  
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(formData); }}>
      {formSchema.form_fields.map(field => {
        if (field.field_type === 'html') {
          return <SafeHTMLField key={field.id} field={field} />;
        }
        
        // Other field types collect data
        return (
          <OtherFieldComponent
            key={field.id}
            field={field}
            value={formData[field.id]}
            onChange={(id, value) => setFormData(prev => ({...prev, [id]: value}))}
          />
        );
      })}
      
      <button type="submit">Submit</button>
    </form>
  );
};
```

## ⚠️ Best Practices

### DO:
- ✅ Sanitize all HTML content
- ✅ Use semantic HTML structure
- ✅ Make content accessible
- ✅ Keep content concise and relevant
- ✅ Test across different screen sizes

### DON'T:
- ❌ Include executable scripts
- ❌ Use inline styles extensively
- ❌ Trust unsanitized HTML from external sources
- ❌ Make content overly complex
- ❌ Include sensitive information

HTML fields provide rich content display capabilities while maintaining security and accessibility in headless form implementations.
