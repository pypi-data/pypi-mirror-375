from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from django.db import models

from headless_waf_builder.models.abstract_advanced_form import AbstractAdvancedForm


class FormPage(AbstractAdvancedForm):

    use_google_recaptcha = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        help_text='Please tick this option to enable Google Recaptcha'
    )

    content_panels = Page.content_panels + AbstractAdvancedForm.content_panels + [
        FieldPanel('use_google_recaptcha')
    ]

    settings_panels = Page.settings_panels + AbstractAdvancedForm.settings_panels

    # Override preview for headless usage
    def serve_preview(self, request, mode_name):
        """
        Disable preview for headless forms. Returns a simple message instead of trying to render templates.
        """
        from django.http import HttpResponse
        return HttpResponse(
            "<h1>Preview Disabled</h1>"
            "<p>This is a headless form - preview functionality is disabled.</p>"
            "<p>Use the REST API endpoints to interact with this form at <a target='_blank' href='/api/docs'>api/docs</a>.</p>",
            content_type="text/html"
        )
