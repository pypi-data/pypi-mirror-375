from django.utils.html import format_html_join
from wagtail import hooks
from wagtail.admin.staticfiles import versioned_static


@hooks.register('insert_editor_js')
def editor_js():
    js_files = [
        'headless_waf_builder/js/admin.js', # https://fireworks.js.org
    ]
    js_includes = format_html_join('\n', '<script src="{0}"></script>',
        ((versioned_static(filename),) for filename in js_files)
    )
    return js_includes
