# Headless Wagtail Advanced Form Builder

A powerful, headless-first extension to Wagtail's built-in Form Builder that provides advanced form functionality via REST API.

## 🚀 Key Features

- **Headless-First**: Complete REST API for modern frontend frameworks (React, Vue, Next.js, etc.)
- **Advanced Conditional Logic**: Show/hide fields based on other field values
- **Rich Field Types**: 12+ field types including validation, conditional display, and custom widgets
- **Email Integration**: Automatic email notifications with customizable templates  
- **reCAPTCHA Support**: Built-in Google reCAPTCHA v2 integration
- **Docker Ready**: Production-ready Docker configuration included
- **API Documentation**: Interactive Swagger/OpenAPI documentation at `/api/docs`

## 🎯 Perfect For

- **Modern Web Applications**: React, Vue, Angular, Svelte frontends
- **Mobile Applications**: iOS, Android, React Native, Flutter
- **Jamstack Sites**: Next.js, Nuxt.js, Gatsby, Astro
- **Microservices**: Form handling as a dedicated service
- **Headless CMS**: Wagtail admin for form management, API for everything else

## 🔗 Quick Links

- [Installation Guide](getting_started/installing.md) - Get started with Docker or pip install
- [API Documentation](headless/api.md) - Complete REST API reference
- [Field Types](fields/basic_field.md) - All available form field types
- [Live API Demo](/api/docs) - Interactive API documentation

## 💡 How It Works

1. **Create Forms**: Use Wagtail admin to build forms with conditional logic
2. **API Access**: Frontend applications consume forms via REST API
3. **Submit Data**: Post form submissions through secure API endpoints
4. **Process Results**: Automatic email notifications and data handling

This system completely eliminates the need for Django templates - everything is handled through clean REST API endpoints.
