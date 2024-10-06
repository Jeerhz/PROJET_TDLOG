from django import forms
from django.utils.safestring import mark_safe

class SelectSearch(forms.Select):
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    def render(self, name, value, attrs=None, renderer=None):
        # Call the parent class's render method
        if attrs is None:
            attrs = {}

        final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        id_for_label = final_attrs.get('id', None)
        original_render = super().render(name, value, attrs, renderer)
        # Add some custom HTML before or after the original render
        custom_html = f'<input type="text" placeholder="Nom client" class="form-control select-search" size="30" data-idselect="{id_for_label}">{original_render}'
        
        # Mark the custom HTML as safe for rendering (so Django doesn't escape it)
        return mark_safe(custom_html)
