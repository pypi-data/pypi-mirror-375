# Custom Page Models for Headless Development

Learn how to create custom form page models that extend the headless functionality.

## 🏗️ Why Custom Models?

While the built-in `FormPage` and `EmailFormPage` work great out of the box, you might want custom models for:

- **Additional Fields**: Add custom metadata, settings, or content fields
- **Custom Logic**: Implement specialized validation or processing
- **API Extensions**: Add custom API endpoints or response data
- **Integration**: Connect with external services or databases
- **Branding**: Add organization-specific fields and behaviors

---

## 🚀 Basic Custom Form Page

### Create Your Custom Model

```python
# models.py
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page

from headless_waf_builder.models import AbstractAdvancedForm


class CustomFormPage(AbstractAdvancedForm):
    # Add custom fields
    form_category = models.CharField(
        max_length=100,
        default="general",
        help_text="Category for organizing forms"
    )
    
    api_webhook_url = models.URLField(
        blank=True,
        help_text="Optional webhook URL to call after form submission"
    )
    
    enable_analytics = models.BooleanField(
        default=True,
        help_text="Track form submissions in analytics"
    )

    # Configure admin panels
    content_panels = Page.content_panels + AbstractAdvancedForm.content_panels + [
        MultiFieldPanel([
            FieldPanel('form_category'),
            FieldPanel('api_webhook_url'),
            FieldPanel('enable_analytics'),
        ], heading="Custom Settings")
    ]

    # Disable preview for headless usage
    preview_modes = []

    def serve_preview(self, request, mode_name):
        from django.http import HttpResponse
        return HttpResponse(
            "<h1>Preview Disabled</h1>"
            "<p>This is a headless form - use the API endpoints.</p>"
            "<p><a href='/api/docs' target='_blank'>View API Documentation</a></p>",
            content_type="text/html"
        )

    class Meta:
        verbose_name = "Custom Form Page"
```

### Custom API Response

Override the API serialization to include your custom fields:

```python
# api/schemas.py
from pydantic import BaseModel
from typing import Optional

class CustomFormPageSchema(BaseModel):
    # Include all standard fields
    id: int
    title: str
    slug: str
    url_path: str
    form_fields: list
    submit_button_text: str
    
    # Add your custom fields
    form_category: str
    api_webhook_url: Optional[str] = None
    enable_analytics: bool = True
    
    class Config:
        from_attributes = True  # For Pydantic v2

# api/router.py - extend the router
from .schemas import CustomFormPageSchema

@api.get("/custom_form/{form_id}")
def get_custom_form(request, form_id: int):
    try:
        form = CustomFormPage.objects.get(id=form_id)
        return CustomFormPageSchema.from_orm(form)
    except CustomFormPage.DoesNotExist:
        return 404, {"message": "Form not found"}
```

---

## 📧 Custom Email Form Page

### Advanced Email Configuration

```python
# models.py
from headless_waf_builder.models import AbstractAdvancedEmailForm

class CustomEmailFormPage(AbstractAdvancedEmailForm):
    # Multiple recipient support
    cc_addresses = models.TextField(
        blank=True,
        help_text="CC email addresses (one per line)"
    )
    
    bcc_addresses = models.TextField(
        blank=True, 
        help_text="BCC email addresses (one per line)"
    )
    
    # Email template customization
    email_template_name = models.CharField(
        max_length=200,
        default="emails/custom_form_submission.html",
        help_text="Custom email template path"
    )
    
    # Auto-responder
    send_auto_reply = models.BooleanField(
        default=False,
        help_text="Send automatic reply to form submitter"
    )
    
    auto_reply_subject = models.CharField(
        max_length=255,
        blank=True,
        default="Thank you for your submission"
    )

    content_panels = AbstractAdvancedEmailForm.content_panels + [
        MultiFieldPanel([
            FieldPanel('cc_addresses'),
            FieldPanel('bcc_addresses'),
            FieldPanel('email_template_name'),
        ], heading="Advanced Email Settings"),
        
        MultiFieldPanel([
            FieldPanel('send_auto_reply'),
            FieldPanel('auto_reply_subject'),
        ], heading="Auto-Responder")
    ]

    def process_form_submission(self, form):
        """Override to add custom processing logic"""
        # Call parent method for standard processing
        result = super().process_form_submission(form)
        
        # Add custom logic
        if self.api_webhook_url:
            self.call_webhook(form.cleaned_data)
            
        if self.send_auto_reply and 'email' in form.cleaned_data:
            self.send_auto_reply_email(form.cleaned_data)
            
        return result

    def call_webhook(self, form_data):
        """Call external webhook with form data"""
        import requests
        try:
            requests.post(self.api_webhook_url, json={
                'form_id': self.id,
                'form_title': self.title,
                'submission_data': form_data
            }, timeout=10)
        except requests.RequestException:
            # Log error but don't fail the form submission
            pass

    def send_auto_reply_email(self, form_data):
        """Send automatic reply to form submitter"""
        from django.core.mail import send_mail
        
        try:
            send_mail(
                subject=self.auto_reply_subject,
                message=f"Thank you for contacting us, {form_data.get('name', 'there')}!",
                from_email=self.from_address,
                recipient_list=[form_data['email']],
                fail_silently=True
            )
        except Exception:
            # Log error but don't fail the form submission
            pass
```

---

## 🔧 Custom Field Types

### Add Custom Form Fields

```python
# models.py
from headless_waf_builder.models import AbstractAdvancedFormField

class CustomFormField(AbstractAdvancedFormField):
    # Add custom field properties
    placeholder_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Placeholder text for the field"
    )
    
    css_classes = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom CSS classes for styling"
    )
    
    data_attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom data attributes as JSON"
    )

# Link to your custom form page
class CustomFormPage(AbstractAdvancedForm):
    form_field = CustomFormField  # Use custom field model
```

### Custom Field in API Response

```python
# Include custom field data in API responses
def get_form_fields_data(self):
    """Override to include custom field properties"""
    fields_data = []
    for field in self.get_form_fields():
        field_data = {
            'id': field.clean_name,
            'label': field.label,
            'field_type': field.field_type,
            'required': field.required,
            'help_text': field.help_text,
            # Add custom properties
            'placeholder_text': getattr(field, 'placeholder_text', ''),
            'css_classes': getattr(field, 'css_classes', ''),
            'data_attributes': getattr(field, 'data_attributes', {}),
        }
        fields_data.append(field_data)
    return fields_data
```

---

## 🎯 Advanced API Integration

### Custom API Endpoints

```python
# api/custom_router.py
from ninja import Router
from django.shortcuts import get_object_or_404

custom_api = Router()

@custom_api.get("/forms/category/{category}")
def forms_by_category(request, category: str):
    """Get all forms in a specific category"""
    forms = CustomFormPage.objects.filter(
        form_category=category,
        live=True
    ).values('id', 'title', 'slug', 'url_path')
    
    return list(forms)

@custom_api.get("/forms/{form_id}/analytics")
def form_analytics(request, form_id: int):
    """Get form submission analytics"""
    form = get_object_or_404(CustomFormPage, id=form_id)
    
    if not form.enable_analytics:
        return 403, {"message": "Analytics disabled for this form"}
    
    # Return analytics data
    return {
        "total_submissions": form.get_submission_count(),
        "submissions_this_month": form.get_monthly_submissions(),
        "conversion_rate": form.calculate_conversion_rate(),
    }

# Add to main router
# api/router.py
from .custom_router import custom_api
api.add_router("/custom", custom_api)
```

### Frontend Usage

```javascript
// Get forms by category
const contactForms = await fetch('/api/custom/forms/category/contact')
  .then(r => r.json());

// Get form analytics
const analytics = await fetch('/api/custom/forms/123/analytics')
  .then(r => r.json());
```

---

## 🏠 Homepage Integration

### Allow Forms as Subpages

```python
# models.py
from wagtail.models import Page

class HomePage(Page):
    subpage_types = [
        'CustomFormPage',
        'CustomEmailFormPage', 
        # Other page types...
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        
        # Add forms data for API discovery
        context['available_forms'] = [
            {
                'title': form.title,
                'slug': form.slug,
                'url_path': form.url_path,
                'category': form.form_category,
                'api_endpoint': f'/api/form_by_path{form.url_path.rstrip("/")}'
            }
            for form in CustomFormPage.objects.child_of(self).live()
        ]
        
        return context
```

### API Endpoint for Form Discovery

```python
@api.get("/forms/discover")
def discover_forms(request):
    """Discover all available forms"""
    return [
        {
            'id': form.id,
            'title': form.title,
            'category': form.form_category,
            'url_path': form.url_path,
            'api_endpoint': f'/api/form_by_path{form.url_path.rstrip("/")}'
        }
        for form in CustomFormPage.objects.live()
    ]
```

---

## 🚀 Best Practices

### 1. Keep Models Focused
- One responsibility per model
- Use composition over inheritance when possible
- Keep API responses lightweight

### 2. Error Handling
```python
def process_form_submission(self, form):
    try:
        result = super().process_form_submission(form)
        # Custom logic with proper error handling
        return result
    except Exception as e:
        # Log error but don't break the user experience
        logger.error(f"Custom processing failed: {e}")
        return result
```

### 3. Performance Optimization
```python
# Use select_related and prefetch_related
def get_api_data(self):
    return self.__class__.objects.select_related('parent').prefetch_related(
        'form_fields'
    ).get(id=self.id)
```

### 4. API Versioning
```python
# Consider API versioning for breaking changes
@api.get("/v2/form_by_path/{path}")
def form_by_path_v2(request, path: str):
    # Updated API with new features
    pass
```

---

## ✅ Testing Custom Models

```python
# tests.py
from django.test import TestCase
from rest_framework.test import APIClient

class CustomFormPageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.form_page = CustomFormPage.objects.create(
            title="Test Form",
            slug="test-form",
            form_category="test"
        )
    
    def test_custom_api_endpoint(self):
        response = self.client.get(f'/api/custom/forms/{self.form_page.id}/analytics')
        self.assertEqual(response.status_code, 200)
    
    def test_webhook_integration(self):
        # Test webhook calling logic
        pass
```

This approach gives you complete control over your headless form system while maintaining all the powerful features of the base package.        
            
            
