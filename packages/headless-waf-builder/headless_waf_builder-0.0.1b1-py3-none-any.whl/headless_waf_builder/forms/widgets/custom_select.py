from django.forms import Select


class CustomSelect(Select):
    """
    Temporarily fixes an issue with wagtail whereby select dropdowns are not getting selected correctly due to a
    missing wrapping div
    """
    template_name = "headless_waf_builder/widgets/custom_select.html"
