# wagtail-custom-code-editor
![Wagtail Custom Code Editor Workflow](https://github.com/ammein/wagtail-custom-code-editor/actions/workflows/github-actions-check.yml/badge.svg)

A **Wagtail Custom Code Editor Field** for your own editor field.

This package adds a full-featured code editor that is perfect for coding tutorials, documentation containing code examples, or any other type of page that needs to display code.

This field uses the open-source Ace Editor library that you may found here [Ace Editor](https://ace.c9.io/)

![intro](https://raw.githubusercontent.com/ammein/wagtail-custom-code-editor/refs/heads/main/docs/intro.gif)

## Features
- Replace traditional textarea to Ace Editor that you can easily check the linting of the codes.
- Add snippet for better re-usable small region of source code, or any text format.
- Configure your own Ace Editor Options to your own editor preferences.
- Easily change mode available on your own default/custom mode's setup.
- You can save any code highlights so that it can retain the same highlight's code when you change to different mode.

## Documentation
- [Settings](https://github.com/ammein/wagtail-custom-code-editor/blob/main/docs/settings.md)
- [Widget Options](https://github.com/ammein/wagtail-custom-code-editor/blob/main/docs/options.md)
- [Change Modes](https://github.com/ammein/wagtail-custom-code-editor/blob/main/docs/modes.md)
- [Django Admin](https://github.com/ammein/wagtail-custom-code-editor/blob/main/docs/django-admin.md)
- [Extend JS Functionality](https://github.com/ammein/wagtail-custom-code-editor/blob/main/docs/extend-functionality.md)

## Install
Simply install in your project:
```shell
pip install wagtail-custom-code-editor
```

In your settings, add the package in `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    "wagtail_custom_code_editor",
    ...
]
```

### Usage

#### Field
You can easily add the `CustomCodeEditorField` to your model fields like this:
```python
from wagtail_custom_code_editor.fields import CustomCodeEditorField

class MyPage(Page):
    code = CustomCodeEditorField()
    ...
```
> The field is using [Django's JSONField](https://docs.djangoproject.com/en/5.1/ref/models/fields/#django.db.models.JSONField)

#### Panel
Then you add `CustomCodeEditorPanel` like this:

```python
from wagtail_custom_code_editor.panels import CustomCodeEditorPanel
from wagtail_custom_code_editor.fields import CustomCodeEditorField

class MyPage(Page):
    code = CustomCodeEditorField()

    content_panels = Page.content_panels + [
        CustomCodeEditorPanel('code')
    ]
```

#### Block
You can also add as `CustomCodeEditorBlock` like this:

```python
from wagtail_custom_code_editor.blocks import CustomCodeEditorBlock
from wagtail.blocks import (
    StructBlock,
)

class CodeBlock(StructBlock):
    code = CustomCodeEditorBlock()
```

#### Frontend
You can easily grab the JSON value like this:
```html
<pre><code>{{ page.code.code }}</code></pre>
```

The JSON returns this two key value:
```json
{
  "code": "Any Code here",
  "mode": "html" 
}
```

## License

wagtail-custom-code-editor is released under the [MIT License](http://www.opensource.org/licenses/MIT).