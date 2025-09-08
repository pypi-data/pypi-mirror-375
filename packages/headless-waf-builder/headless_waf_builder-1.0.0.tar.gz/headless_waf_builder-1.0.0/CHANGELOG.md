# Changelog

All notable changes to Headless WAF Builder will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-08 🎉 **MAJOR RELEASE**

### 🚀 **Wagtail Advanced Form Builder Headless API Support**

This is a major milestone release introducing comprehensive headless API capabilities, making Headless WAF Builder the first headless-first form builder package designed specifically for modern frontend frameworks with complete REST API integration.

#### **Added**
- **🌐 Django Ninja REST API Integration**
  - Complete REST API with automatic OpenAPI documentation
  - Interactive API documentation at `/api/docs`
  - Type-safe request/response handling with Pydantic schemas

- **📋 Form Retrieval API**
  - `GET /api/form_by_path/{path}` - Retrieve complete form schemas
  - Full field definitions with validation rules and conditional logic
  - Support for both FormPage and EmailFormPage types
  - Comprehensive error handling with detailed HTTP status codes

- **📤 Form Submission API**
  - `POST /api/form_by_path/` - Submit form data with validation
  - Automatic server-side validation with detailed error responses
  - Background email processing with Celery integration
  - Custom thanks page content in API responses

- **🔒 Enterprise-Grade Security**
  - CSRF token protection with `GET /api/csrf/` endpoint
  - Google reCAPTCHA v2 and v3 integration
  - IP-based rate limiting and validation
  - Secure token handling and validation

- **📝 Complete Schema System**
  - Pydantic schemas for all 14+ field types
  - Type-safe field definitions with validation rules
  - Conditional logic rules serialization
  - Union types for polymorphic form handling

#### **Enhanced Field Support**
- **📞 Phone Field** - International phone number validation
- **📅 Simple Date Field** - Date picker with age validation (minimum/maximum age)
- **🎨 Improved HTML Field** - Rich content with enhanced sanitization
- **🔢 Enhanced Number Field** - Better validation and formatting
- **✅ Advanced Checkbox Groups** - Side-by-side layouts and custom styling

#### **Conditional Logic Engine Improvements**
- **Enhanced Rule Validation** - More robust conditional logic processing
- **Cross-Field Dependencies** - Complex field relationships
- **Real-time Rule Processing** - Instant field visibility updates
- **Multiple Condition Support** - AND/OR logic combinations

#### **Developer Experience**
- **📖 Auto-Generated Documentation** - Complete API reference with examples
- **🛠️ Easy Integration** - Simple URL configuration for API endpoints
- **🎯 Type Safety** - Full TypeScript-compatible schema definitions
- **📱 Frontend Framework Ready** - Works with React, Vue, Angular, and more

#### **Background Processing**
- **⚡ Celery Integration** - Asynchronous email sending
- **📧 Enhanced Email System** - Improved email templates and processing
- **🔄 Task Queue Management** - Reliable background job processing

### **Changed**
- **🏗️ Architecture Modernization**
  - Upgraded to support Wagtail 6.X.X as primary target
  - Django 4.2+ requirement for enhanced security and performance
  - Modular package structure for better maintainability

- **📦 Dependency Management**
  - Added optional `headless` extra for API dependencies
  - `pip install wagtail-advanced-form-builder[headless]` for full API support
  - Core package remains lightweight for traditional Wagtail usage

### **Security**
- **🔐 CSRF Protection** - Comprehensive cross-site request forgery protection
- **🛡️ Input Sanitization** - Enhanced XSS protection for all field types
- **🔍 Validation Enhancement** - Stronger server-side validation
- **📊 Rate Limiting** - Protection against abuse and spam

### **Documentation**
- **📚 Complete API Documentation** - Comprehensive guides and examples
- **🚀 Quick Start Guides** - Step-by-step setup for both traditional and headless usage
- **💡 Code Examples** - Real-world implementation examples for popular frameworks
- **🎯 Best Practices** - Security, performance, and architectural guidance

### **Installation Guide**
For new installations:
1. Install the package: `pip install headless-waf-builder`
2. Add to INSTALLED_APPS: `'wagtail_advanced_form_builder'`
3. Add API URLs to your `urls.py`: `path("api/", wagtail_advanced_form_builder_api.urls)`
4. Run migrations: `python manage.py migrate`

**Optional extras**:
- For reCAPTCHA and background processing: `pip install headless-waf-builder[full]`

**Note**: This is a brand new headless-first package, completely separate from the original wagtail-advanced-form-builder.

---

## **Future Roadmap**

### Planned for 1.1.0
- **🔌 Webhook Integration** - Real-time form submission notifications
- **📊 Analytics API** - Form performance and submission analytics
- **🎨 Theme System** - Customizable form styling via API
- **🔄 Form Versioning** - Track form changes and rollback capabilities

### Planned for 1.2.0
- **🌍 Multi-language Support** - Internationalization for form fields
- **📱 Mobile SDKs** - Native iOS and Android form rendering
- **🔗 Third-party Integrations** - Salesforce, HubSpot, Mailchimp connectors
- **📈 Advanced Analytics** - Conversion tracking and A/B testing

---

## **Contributors**

Special thanks to all contributors who made this major release possible:

- **Richard Blake** ([Octave](https://octave.nz)) - Project Lead & Architecture
- **Community Contributors** - Bug reports, feature requests, and testing

---

*This release represents over 6 months of development and testing to deliver the most comprehensive form building solution for Wagtail CMS with modern headless capabilities.* 