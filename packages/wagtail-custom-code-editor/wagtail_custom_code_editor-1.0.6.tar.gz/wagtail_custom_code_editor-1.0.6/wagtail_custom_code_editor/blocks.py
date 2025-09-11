from __future__ import annotations
from django import forms
from wagtail.blocks import FieldBlock
from .validators import CustomCodeEditorDecoder
from .widgets import CustomCodeEditorWidget


class CustomCodeEditorBlock(FieldBlock):
    def __init__(
            self,
            mode=None,
            theme=None,
            width="100%",
            height="500px",
            font_size=None,
            keybinding=None,
            useworker=True,
            extensions=None,
            enable_options=True,
            enable_modes=False,
            dropdown_config=None,
            read_only_config=None,
            save_command_config=None,
            options=None,
            modes=None,
            attrs=None,
            **kwargs,
    ):
        self._ace_options = {
            "mode": mode,
            "theme": theme,
            "width": width,
            "height": height,
            "font_size": font_size,
            "keybinding": keybinding,
            "useworker": useworker,
            "extensions": extensions,
            "enable_options": enable_options,
            "enable_modes": enable_modes,
            "dropdown_config": dropdown_config,
            "read_only_config": read_only_config,
            "save_command_config": save_command_config,
            "options": options,
            "modes": modes,
            "attrs": attrs,
            "block": True
        }
        self.field = forms.JSONField(widget=CustomCodeEditorWidget(**self._ace_options), decoder=CustomCodeEditorDecoder, **kwargs)
        super().__init__(**kwargs)

    class Meta:
        icon = 'code'
