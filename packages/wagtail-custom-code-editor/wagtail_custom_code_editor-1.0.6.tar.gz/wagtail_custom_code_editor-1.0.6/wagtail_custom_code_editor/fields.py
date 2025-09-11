from django.db import models

from .validators import CustomCodeEditorDecoder


class CustomCodeEditorField(models.JSONField):
    description = "Custom Code Editor"

    def __init__(self, *args, **kwargs):
        kwargs['decoder'] = CustomCodeEditorDecoder
        super().__init__(*args, **kwargs)
