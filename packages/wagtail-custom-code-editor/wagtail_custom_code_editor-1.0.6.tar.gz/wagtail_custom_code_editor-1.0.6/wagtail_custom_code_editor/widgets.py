from __future__ import unicode_literals, annotations

import re
import json
from typing import Dict, List, Any
from django.utils.functional import cached_property
from django.forms import Media, widgets
from wagtail.admin.telepath.widgets import WidgetAdapter
from wagtail.admin.telepath import register
from .settings import wagtail_custom_code_editor_settings
from .files import (
    EXTENSIONS,
    MODES,
    WORKERS
)


class CustomCodeEditorWidget(widgets.Widget):
    template_name = 'code.html'

    def __init__(
            self,
            mode="html",
            theme="chrome",
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
            django_admin=False,
            block=False
    ):
        self.mode: str = mode
        self.theme: str = theme
        self.width: str = width
        self.height: str = height
        self.font_size: str = font_size
        self.keybinding: str = keybinding
        self.useworker: bool = useworker
        self.extensions: str | List = extensions
        self.enable_options: bool = enable_options
        self.enable_modes: bool = enable_modes
        self.dropdown_config = dropdown_config or {}
        self.read_only_config = read_only_config or {}
        self.save_command_config = save_command_config or {}
        self.django_admin: bool = django_admin
        self.block: bool = block

        self.original_options = json.loads(options) if isinstance(options, str) else options

        # Merge by key 'name' matches the value of options
        self.options: Dict[str, Any] = [{**d, "defaultValue": self.original_options[d['name']]} if d['name'] in self.original_options else d for d in getattr(wagtail_custom_code_editor_settings, "OPTIONS_TYPES")] if bool(self.original_options) is not False else getattr(wagtail_custom_code_editor_settings, "OPTIONS_TYPES")

        # Merge by key 'name' matches the value of modes
        self.modes: List[Dict[str, str]] = list(
            {d['name']: d for d in
             getattr(wagtail_custom_code_editor_settings, "MODES") + modes}.values()) if modes is not None else getattr(
            wagtail_custom_code_editor_settings, "MODES")

        # See if mode not available in modes
        if len([d for d in self.modes if d['name'] == self.mode]) == 0:
            self.modes.append({
                "name": self.mode,
                "title": self.mode.capitalize(),
                "snippet": "@code-here"
            })

        super(CustomCodeEditorWidget, self).__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['width'] = self.width
        context['widget']['height'] = self.height
        context['widget']['font_size'] = self.font_size
        context['widget']['enable_modes'] = bool(self.enable_modes)
        context['widget']['enable_options'] = bool(self.enable_options)
        context['widget']['options'] = self.options
        context['widget']['modes'] = self.modes
        context['widget']['django_admin'] = bool(self.django_admin)
        return context

    @cached_property
    def media(self):
        js = [
            "wagtail_custom_code_editor/ace/ace.js",
            "wagtail_custom_code_editor/js/custom-code-editor.js",
            "wagtail_custom_code_editor/clipboard/clipboard.min.js",
        ]

        if not self.django_admin:
            js.append("wagtail_custom_code_editor/js/custom-code-editor-controller.js")

        save_modes = []

        # For Mode Files
        if self.enable_modes:
            for modes in self.modes:
                for key, val in modes.items():
                    if key == "name":
                        js.append("wagtail_custom_code_editor/ace/mode-%s.js" % val)
                        save_modes.append(val)
        else:
            js.append("wagtail_custom_code_editor/ace/mode-%s.js" % self.mode)

        # For Theme Files
        if self.theme:
            js.append("wagtail_custom_code_editor/ace/theme-%s.js" % self.theme)

        # For Keybinding
        if self.keybinding:
            js.append("wagtail_custom_code_editor/ace/keybinding-%s.js" % self.keybinding)

        # For Snippets
        if len(save_modes) > 0:
            for mode in save_modes:
                if mode + ".js" in MODES:
                    js.append("wagtail_custom_code_editor/ace/snippets/%s.js" % mode)

        # For EXT Files
        if self.extensions:
            if isinstance(self.extensions, str):
                js.append("wagtail_custom_code_editor/ace/ext-%s.js" % self.extensions)
            else:
                for extension in self.extensions:
                    js.append("wagtail_custom_code_editor/ace/ext-%s.js" % extension)
        else:
            # Upload all extensions by default
            for ext in EXTENSIONS:
                js.append("wagtail_custom_code_editor/ace/%s" % ext)

        # For worker if available
        if self.useworker:
            for worker in WORKERS:
                valid = re.search(r'(?=worker-).*(?=.js)', worker)
                if valid:
                    worker_val = re.search(r'(?!worker-)\w+(?!.js)$', valid.group())
                    if worker_val and worker_val.group() in save_modes:
                        js.append("wagtail_custom_code_editor/ace/%s" % worker)

        css = {"screen": ["wagtail_custom_code_editor/css/code.css"]}

        return Media(js=js, css=css)

    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        if not self.block:
            attrs['data-controller'] = "custom-code-editor"
        attrs['data-mode-value'] = self.mode
        attrs['data-theme-value'] = self.theme
        attrs['data-width-value'] = self.width
        attrs['data-height-value'] = self.height
        attrs['data-font-size'] = self.font_size or ""
        attrs['data-modes-value'] = json.dumps(self.modes)
        attrs['data-options-value'] = json.dumps(self.options)
        attrs['data-dropdown-config-value'] = json.dumps(self.dropdown_config)
        attrs['data-read-only-config-value'] = json.dumps(self.read_only_config)
        attrs['data-save-command-config-value'] = json.dumps(self.save_command_config)
        attrs['data-original-options-value'] = json.dumps(self.original_options)
        return attrs

    def format_value(self, value):
        if value is None or value == 'null':
            return json.dumps({
                "code": None,
                "mode": self.mode
            })

        return value


class CustomCodeEditorAdapter(WidgetAdapter):
    js_constructor = 'wagtail_custom_code_editor.widgets.CustomCodeEditor'

    def js_args(self, widget):
        args = super().js_args(widget)
        return [
            *args
        ]

    class Media:
        js = ['wagtail_custom_code_editor/js/custom-code-editor-block-widget.js']


register(CustomCodeEditorAdapter(), CustomCodeEditorWidget)
