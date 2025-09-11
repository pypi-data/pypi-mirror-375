import json
from django.core.exceptions import ValidationError


# https://brettbeeson.com.au/encode-custom-models-to-djangos-jsonfield/
class CustomCodeEditorDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(dct):
        if "code" in dct and "mode" in dct:
            return dct
        else:
            raise ValidationError(
                'Invalid value of Custom Code Editor',
                code='invalid',
                params={
                    'value': dct
                }
            )
