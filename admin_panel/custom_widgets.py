# admin_panel/custom_widgets.py
from django.forms.widgets import ClearableFileInput

class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs.update({'multiple': 'multiple'})

    def value_from_datadict(self, data, files, name):
        upload = files.getlist(name)
        if not upload:
            return []
        return upload
