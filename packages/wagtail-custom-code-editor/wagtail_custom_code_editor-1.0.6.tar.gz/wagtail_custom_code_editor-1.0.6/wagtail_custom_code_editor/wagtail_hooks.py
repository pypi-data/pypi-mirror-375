from django.utils.html import format_html
from .settings import wagtail_custom_code_editor_settings
from django.utils.safestring import mark_safe

from wagtail import hooks


@hooks.register('insert_global_admin_js')
def editor_js():
    emmet_url = getattr(wagtail_custom_code_editor_settings, "EMMET_URL")
    if emmet_url:
        return mark_safe(format_html('<script src="{}"></script>', emmet_url))
