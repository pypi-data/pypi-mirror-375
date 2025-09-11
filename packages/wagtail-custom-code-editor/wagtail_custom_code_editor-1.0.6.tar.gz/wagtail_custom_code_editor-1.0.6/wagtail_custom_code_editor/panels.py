from wagtail.admin.panels import FieldPanel
from .widgets import CustomCodeEditorWidget


class CustomCodeEditorPanel(FieldPanel):
    def __init__(
            self,
            field_name,
            *args,
            **kwargs
    ):
        self.ace_options = {
            "mode": kwargs.pop('mode', 'html'),
            "theme": kwargs.pop('theme', 'chrome'),
            "width": kwargs.pop('width', "100%"),
            "height": kwargs.pop('height', '500px'),
            "font_size": kwargs.pop('font_size', None),
            "keybinding": kwargs.pop('keybinding', None),
            "useworker": kwargs.pop('useworker', None),
            "extensions": kwargs.pop('extensions', None),
            "enable_options": kwargs.pop('enable_options', True),
            "enable_modes": kwargs.pop('enable_modes', False),
            "dropdown_config": kwargs.pop('dropdown_config', None),
            "read_only_config": kwargs.pop('read_only_config', None),
            "save_command_config": kwargs.pop('save_command_config', None),
            "options": kwargs.pop('options', None),
            "modes": kwargs.pop('modes', None),
            "attrs": kwargs.pop('attrs', None)
        }
        super().__init__(field_name, *args, **kwargs)

    # To enable cloning with the same ace options attributes using class instance
    def clone(self):
        instance = super().clone()
        instance.ace_options = self.ace_options
        return instance

    def get_form_options(self):
        opts = super().get_form_options()
        opts['widgets'] = {
            self.field_name: CustomCodeEditorWidget(**self.ace_options)
        }
        return opts
