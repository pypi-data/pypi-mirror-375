import warnings
from django.conf import settings
from django.test.signals import setting_changed

DEFAULTS = {
    "EMMET_URL": "https://cloud9ide.github.io/emmet-core/emmet.js",
    # MODES
    "MODES": [
        {
            "title": "Bash",
            "name": "sh",
            "snippet": """
                #!/bin/bash
                # GNU bash, version 4.3.46
                @code-here
            """
        },
        {
            "title": "ActionScript",
            "name": "actionscript"
        },
        {
            "title": "C++",
            "name": "c_cpp",
            "snippet": """
                //Microsoft (R) C/C++ Optimizing Compiler Version 19.00.23506 for x64
                #include <iostream>
        
                int main()
                {
                   @code-here
                }
            """
        },
        {
            "title": "C#",
            "name": "csharp",
            "snippet": """
                //Rextester.Program.Main is the entry point for your code. Don't change it.
                //Compiler version 4.0.30319.17929 for Microsoft (R) .NET Framework 4.5
            
                using System;
                using System.Collections.Generic;
                using System.Linq;
                using System.Text.RegularExpressions;
            
                namespace Rextester
                {
                   public class Program
                   {
                      public static void Main(string[] args)
                      {
                            // code goes here
                            @code-here
                      }
                   }
                }
            """
        },
        {
            "name": "php",
            "snippet": """
                <html>
                <head>
                <title>PHP Test</title>
                </head>
                <body>
                <?php //code goes here
                   @code-here
                ?> 
                </body>
                </html>
            """
        },
        {
            "name": "html",
            "snippet": """
                <!DOCTYPE html>
                <html>
                <head>
                <title>
                    <!-- Title Here -->
                </title>
                </head>
                <body>
                    <!-- Code-here -->
                    @code-here
                </body>
                </html>
            """
        },
        {
            "name": "javascript",
            "snippet": """
                document.addEventListener("DOMContentLoaded" , function(){
                   @code-here
                });
            """
        }
    ],
    # Options
    "OPTIONS_TYPES": [
        {
            "name": "selectionStyle",
            "type": "string",
            "value": ["line", "text"],
            "category": "editor",
        },
        {
            "name": "highlightActiveLine",
            "type": "boolean",
            "value": None,
            "category": "editor",
        },
        {
            "name": "highlightSelectedWord",
            "type": "boolean",
            "value": None,
            "category": "editor",
        },
        {
            "name": "readOnly",
            "type": "boolean",
            "value": None,
            "category": "editor",
        },
        {
            "name": "cursorStyle",
            "type": "string",
            "value": ["ace", "slim", "smooth", "wide"],
            "category": "editor",
        },
        {
            "name": "mergeUndoDeltas",
            "type": "string",
            "value": [
                {"title": "Always", "value": "always"},
                {"title": "Never", "value": False},
                {"title": "Timed", "value": True},
            ],
            "category": "editor",
        },
        {
            "name": "behavioursEnabled",
            "type": "boolean",
            "value": None,
            "category": "editor",
        },
        {
            "name": "wrapBehavioursEnabled",
            "type": "boolean",
            "value": None,
            "category": "editor",
        },
        {
            "name": "autoScrollEditorIntoView",
            "type": "boolean",
            "value": None,
            "help": "This is needed if editor is inside scrollable page",
            "category": "editor",
        },
        {
            "name": "copyWithEmptySelection",
            "type": "boolean",
            "value": None,
            "help": "Copy/Cut the full line if selection is empty, "
                    "defaults to False",
            "category": "editor",
        },
        {
            "name": "useSoftTabs",
            "type": "boolean",
            "value": None,
            "category": "editor",
        },
        {
            "name": "navigateWithinSoftTabs",
            "type": "boolean",
            "value": None,
            "category": "editor",
        },
        {
            "name": "enableMultiSelect",
            "type": "boolean",
            "value": None,
            "category": "editor",
        },
        {
            "name": "hScrollBarAlwaysVisible",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "vScrollBarAlwaysVisible",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "highlightGutterLine",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "animatedScroll",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "showInvisibles",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "showPrintMargin",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "printMarginColumn",
            "type": "number",
            "value": {"min": 0, "max": 100, "steps": 1},
            "category": "renderer",
        },
        {
            "name": "printMargin",
            "type": "number",
            "value": {"min": 0, "max": 100, "steps": 1},
            "category": "renderer",
        },
        {
            "name": "fadeFoldWidgets",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "showFoldWidgets",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "showLineNumbers",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "showGutter",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "displayIndentGuides",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "scrollPastEnd",
            "type": ["number", "boolean"],
            "value": {"min": 0, "max": 1, "steps": 0.1},
            "help": "Number of page sizes to scroll after document end "
                    "(typical values are 0, 0.5, and 1)",
            "category": "renderer",
        },
        {
            "name": "fixedWidthGutter",
            "type": "boolean",
            "value": None,
            "category": "renderer",
        },
        {
            "name": "scrollSpeed",
            "type": "number",
            "value": {"min": 0, "max": 100, "steps": 1},
            "category": "mouseHandler",
        },
        {
            "name": "dragDelay",
            "type": "number",
            "value": {"min": 0, "max": 200, "steps": 1},
            "category": "mouseHandler",
        },
        {
            "name": "dragEnabled",
            "type": "boolean",
            "value": None,
            "category": "mouseHandler",
        },
        {
            "name": "focusTimeout",
            "type": "number",
            "value": None,
            "category": "mouseHandler",
        },
        {
            "name": "tooltipFollowsMouse",
            "type": "boolean",
            "value": None,
            "category": "mouseHandler",
        },
        {
            "name": "overwrite",
            "type": "boolean",
            "value": None,
            "category": "session",
        },
        {
            "name": "newLineMode",
            "type": "string",
            "value": ["auto", "unix", "windows"],
            "category": "session",
        },
        {
            "name": "tabSize",
            "type": "number",
            "value": {"min": 0, "max": 20, "steps": 1},
            "category": "session",
        },
        {
            "name": "wrap",
            "type": ["boolean", "number"],
            "value": None,
            "category": "session",
        },
        {
            "name": "foldStyle",
            "type": "string",
            "value": ["markbegin", "markbeginend", "manual"],
            "category": "session",
        },
        {
            "name": "enableBasicAutocompletion",
            "type": "boolean",
            "value": None,
            "category": "extension",
        },
        {
            "name": "enableLiveAutocompletion",
            "type": "boolean",
            "value": None,
            "category": "extension",
        },
        {
            "name": "enableEmmet",
            "type": "boolean",
            "value": None,
            "category": "extension",
        },
        {
            "name": "useElasticTabstops",
            "type": "boolean",
            "value": None,
            "category": "extension",
        },
    ]
}

# List of settings that have been deprecated
DEPRECATED_SETTINGS = []

# List of settings that have been removed
# note: use a tuple of (setting, deprecation warning from deprecation.py)
REMOVED_SETTINGS = []


class CustomCodeEditorSettings:
    """
    A settings object that allows the wagtailmedia settings to be accessed as
    properties. For example:
        from wagtail_custom_code_editor.settings import wagtail_custom_code_editor_settings
        print(wagtail_custom_code_editor_settings.MODES)
    Note:
    This is an internal class that is only compatible with settings namespaced
    under the WAGTAIL_CUSTOM_CODE_EDITOR name. It is not intended to be used by 3rd-party
    apps, and test helpers like `override_settings` may not work as expected.
    """

    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = self.__check_user_settings(
                getattr(settings, "WAGTAIL_CUSTOM_CODE_EDITOR", {})
            )
        return self._user_settings

    def __getattr__(self, item):
        if item not in self.defaults:
            raise AttributeError(f"Invalid wagtail_custom_code_editor setting: '{item}'")

        try:
            # Check if present in user settings
            val = self.user_settings[item]
        except KeyError:
            val = self.defaults[item]

        # Cache the result
        self._cached_attrs.add(item)
        setattr(self, item, val)
        return val

    @staticmethod
    def __check_user_settings(user_settings):
        for setting, category in DEPRECATED_SETTINGS:
            if setting in user_settings or hasattr(settings, setting):
                warnings.warn(
                    f"The '{setting}' setting is deprecated and will be removed in the next release, ",
                    category=category,
                    stacklevel=2,
                )

        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(
                    f"The '{setting}' setting has been removed."
                    f"Please refer to the wagtail_custom_code_editor documentation for available settings."
                )

        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


wagtail_custom_code_editor_settings = CustomCodeEditorSettings(None, DEFAULTS)


def reload_wagtail_custom_code_editor_settings(**kwargs):
    setting = kwargs['setting']
    if setting == "WAGTAIL_CUSTOM_CODE_EDITOR":
        wagtail_custom_code_editor_settings.reload()


setting_changed.connect(reload_wagtail_custom_code_editor_settings)
