from django.forms.widgets import ClearableFileInput, Input, CheckboxInput
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape, format_html, html_safe


class ImagePreviewWidget(ClearableFileInput):

    '''Basically a ClearableFileInput widget, but:
         - remove from the template most clutter: we leave only the image, the clear and the <input>
         - we define a class for the input, so that we can hide it with CSS
    '''

    # The "for" in the <label> allows to open the "open file" dialog by clicking on the image, no js involved
    template_with_initial = (
        '<label for=%(id_for_label)s><img id="%(img_id)s" src="/media/%(initial)s" width="100px"></label>'
        '%(clear_template)s<br />%(input)s'
    )

    INPUT_CLASS = 'image-preview'  # This is the class of the <input> element, which we want to hide

    def __init__(self, attrs=None):
        super(ImagePreviewWidget, self).__init__(attrs)
        self.attrs['class'] = self.INPUT_CLASS

    # Override ClearableFileInput:render
    def render(self, name, value, attrs=None):
        id_for_label = self.id_for_label(attrs.get('id'))
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
            # We need the id, so that clicking in the image triggers the "Open file" native window
            'id_for_label': id_for_label,
            #
            'img_id': id_for_label + '_img',
            'initial': self.format_value(value),
        }
        template = '%(input)s'
        substitutions['input'] = Input.render(self, name, value, attrs)  # call Input.render directly

        if self.is_initial(value):
            template = self.template_with_initial
            # substitutions.update(self.get_template_substitution_values(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions
                # substitutions['initial'] = conditional_escape(self.format_value(value))

        return mark_safe(template % substitutions)


class Media:

    css = {
        'all': ('css/image-preview-widget.css',)
    }
    js = ('js/image-preview-widget.js', )