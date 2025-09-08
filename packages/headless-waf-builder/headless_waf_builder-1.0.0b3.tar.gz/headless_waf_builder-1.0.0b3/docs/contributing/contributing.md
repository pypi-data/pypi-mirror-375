# Contributing to Headless Wagtail Advanced Form Builder

We welcome contributions to make this headless form system even better! 🚀

## 🛠️ Development Setup

### Prerequisites
- Docker and Docker Compose
- Git
- Python 3.8+ (for local development)
- Node.js 16+ (if working on documentation)

### Quick Start
1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/headless-wagtail-advanced-form-builder.git
   cd headless-wagtail-advanced-form-builder
   ```

2. **Start development environment**
   ```bash
   docker compose up --build -d
   ```

3. **Access the system**
   - Wagtail Admin: http://localhost:8000/admin (admin/admin123)
   - API Documentation: http://localhost:8000/api/docs
   - MailHog (email testing): http://localhost:8025

### Local Development (Alternative)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[full,dev]"

# Set up environment
cp .env.example .env  # if available
export DJANGO_SETTINGS_MODULE=build_test.settings.dev

# Run migrations and create superuser
python manage.py migrate
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## 🎯 What Can You Contribute?

### 🔧 Core Features
- **New Field Types**: Add specialized form fields
- **API Enhancements**: Improve REST API functionality
- **Validation Logic**: Better form validation
- **Conditional Logic**: Enhanced conditional field display
- **Performance**: Optimization improvements

### 📚 Documentation
- **API Examples**: More frontend integration examples
- **Field Guides**: Detailed field type documentation
- **Tutorials**: Step-by-step implementation guides
- **Best Practices**: Headless development patterns

### 🧪 Testing
- **Unit Tests**: Test coverage improvements
- **API Tests**: REST API endpoint testing
- **Integration Tests**: End-to-end functionality
- **Performance Tests**: Load and stress testing

### 🐛 Bug Fixes
- **API Issues**: REST API bugs and edge cases
- **Form Logic**: Conditional logic problems
- **Validation Bugs**: Field validation issues
- **Admin Interface**: Wagtail admin improvements

## 📋 Contribution Process

### 1. Check Existing Issues
- Look for existing issues on GitHub
- Join the discussion if the issue exists
- Create a new issue if it doesn't exist

### 2. Development Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes.

# Test your changes
python manage.py test
docker compose exec web python manage.py test

# Update documentation if needed

# Commit your changes
git add .
git commit -m "feat: add new feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### 3. Pull Request Guidelines
- **Clear title**: Describe what the PR does
- **Detailed description**: Explain the changes and why
- **Testing**: Include test cases for new features
- **Documentation**: Update docs for user-facing changes
- **API Changes**: Document API changes in PR description

## 🧪 Testing

### Running Tests
```bash
# Run all tests
docker compose exec web python manage.py test

# Run specific test file
docker compose exec web python manage.py test headless_waf_builder.tests.test_api

# Run with coverage
docker compose exec web coverage run --source='.' manage.py test
docker compose exec web coverage report
```

### Test Structure
```
src/headless_waf_builder/tests/
├── test_models.py          # Model tests
├── test_api.py             # API endpoint tests
├── test_forms.py           # Form validation tests
├── test_conditional.py     # Conditional logic tests
└── test_integration.py     # End-to-end tests
```

### Writing Tests
```python
# Example API test
from django.test import TestCase
from rest_framework.test import APIClient
from headless_waf_builder.models import FormPage

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.form_page = FormPage.objects.create(
            title="Test Form",
            slug="test-form"
        )
    
    def test_get_form_by_path(self):
        response = self.client.get('/api/form_by_path/test-form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Test Form')
```

## 📖 Documentation


### Documentation Standards
- **Clear Examples**: Include code examples for all features
- **API First**: Focus on headless/API usage
- **Frontend Agnostic**: Examples for React, Vue, vanilla JS
- **Real-World**: Use practical, realistic examples

## 🏗️ Code Standards

### Python Code Style (recommend)
- **PEP 8**: Follow Python style guidelines
- **Black**: Use black for code formatting
- **isort**: Sort imports properly
- **Type Hints**: Add type hints where beneficial

### API Design Principles
- **RESTful**: Follow REST conventions
- **Consistent**: Consistent response formats
- **Documented**: All endpoints documented
- **Backwards Compatible**: Avoid breaking changes

### Model Design
- **Abstract Base Classes**: Use for shared functionality
- **Headless First**: Avoid template dependencies
- **API Serializable**: Models should serialize cleanly

## 🚀 Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### Creating Releases
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release notes
4. Tag the release
5. Publish to PyPI

## 🤝 Community Guidelines

### Code of Conduct
- **Be Respectful**: Treat everyone with respect
- **Be Inclusive**: Welcome contributors of all backgrounds
- **Be Constructive**: Provide helpful feedback
- **Be Patient**: Remember we're all volunteers

### Getting Help
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check docs first
- **Examples**: Look at example implementations

### Recognition
Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Documentation credits

## 🎯 Priority Areas

We especially welcome contributions in these areas:

### High Priority
- **React/Next.js Examples**: Complete form implementations
- **Vue/Nuxt Examples**: Frontend integration guides
- **Performance Optimization**: API response caching
- **Mobile Examples**: React Native/Flutter integration

### Medium Priority
- **Advanced Validation**: Custom validation rules
- **File Upload Fields**: File handling in headless context
- **Analytics Integration**: Form submission tracking
- **Multi-language Support**: i18n for form fields

### Nice to Have
- **GraphQL API**: Alternative to REST API
- **Webhook System**: Form submission webhooks
- **A/B Testing**: Form variant testing
- **Visual Form Builder**: Drag-drop form creation

## Thank you

Thank you for contributing to making forms better for everyone! 🙌

Every contribution, no matter how small, makes a difference. Whether it's fixing a typo, adding an example, or implementing a major feature, we appreciate your help in making this project better for the entire community.
