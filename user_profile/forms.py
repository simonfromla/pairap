from .models import Profile, Changelog, CredentialImage
from django import forms
# from django.forms import ModelForm, ImageField
from django.forms.models import inlineformset_factory
from django.forms.widgets import FileInput, RadioSelect
# from django.contrib.gis.geos import Point
from .services import prefs_are_none
from django.utils.translation import ugettext as _

from .widgets import ImagePreviewWidget


class PreferenceUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "learn1",
            "learn2",
            "learn3",
            "teach1",
            "teach2",
            "teach3",
            # "public",
        ]

    def clean(self):
        cleaned_data = super(PreferenceUpdateForm, self).clean()
        # form_empty = True
        # for field_value in cleaned_data.values():
        #     print(cleaned_data.items())
        #     # Check for None or '', so IntegerFields with 0 or similar things don't seem empty.
        #     if field_value is not None and field_value != '':
        #         form_empty = False
        #         break
        # if form_empty:
        #     raise forms.ValidationError(_("You must fill at least one field!"))
        return cleaned_data


    def save(self, *args, **kwargs):
        instance = super(PreferenceUpdateForm, self).save(commit=False)
        date = instance.updated
        skills = instance.get_teach()
        instance.save()
        Changelog.objects.create(
            log_date=date,
            owner=instance,
            log_preference=skills
        )
        return instance


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            "introduction",
            "profile_photo",
        ]


class PublicToggleForm(forms.ModelForm):
    # public_toggle = forms.BooleanField(required=False)

    class Meta:
        model = Profile
        fields = [
            "public",
        ]
        labels = {
            'public': ''
        }

    def clean_public(self):
        public_toggle = self.cleaned_data.get("public")
        if public_toggle is True:
            profile = self.instance
            if prefs_are_none(profile):
                profile.public = False
                profile.save()
                raise forms.ValidationError("Try setting some preferences before making your profile public!")
            else:
                profile.public = True
                profile.save()
        #     if prefs are not none, allow
        #         change profile.public = True
        #         return public_toggle
        #     else if prefs are all none
        #         profile.public = False
        #         raise forms.ValidationError("Must fill out prefs")
            # if prefs_are_none(profile):
            #     raise forms.ValidationError("Try offering some skills before making your profile public")
            # else:
            #     profile.public =
        else:
            # TODO: clean
            # Turning public off should happen at will
            self.instance.public = False
            self.instance.save()
        return public_toggle


class PairRequestForm(forms.Form):
    learn_from_partner = forms.ChoiceField(
        choices=[],
        widget=RadioSelect,
        required=False,
        label="What would you like to learn from your partner?"
    )
    teach_to_partner = forms.ChoiceField(
        widget=RadioSelect,
        required=False,
        label="Which skill would you like to share with your partner?"
    )

    def __init__(self, *args, **kwargs):
        learn_choices = kwargs.pop('learn_from_partner')
        teach_choices = kwargs.pop('teach_to_partner')

        super().__init__(*args, **kwargs)
        # .choices must be passed a tuple for ChoiceField
        # So, made each list item a tuple,

        # Opt for template instead of here. Too tightly coupled
        # if not teach_choices:
        #     self.fields['teach_to_partner'].label = "Looks like you have nothing to offer. Send a request anyway?"
        teach_choices = [(x, x) for x in teach_choices]
        learn_choices = [(x, x) for x in learn_choices]
        self.fields['learn_from_partner'].choices = learn_choices
        self.fields['teach_to_partner'].choices = teach_choices


# class PairResponseForm(forms.Form):
#     # go into Pair object and obtain the choices made by the requester.
#     # instantiate form accept, deny (or re-offer buttons(v2)) with choices
#     # Allow for user to check out the requesters profile,
#     # acceptance will begin a chat with them/ redirect to the chat room
#     # chat room with the "contract" hanging above a la simbi
#     pass
    # field = forms.TypedChoiceField(coerce=lambda x: x =='True',
    #                                choices=((False, 'No'), (True, 'Yes')))

    # learn_from_partner = forms.ChoiceField(
    #     choices=[],
    #     widget=RadioSelect,
    #     required=False,
    #     label="What would you like to learn from your partner?"
    # )
    # teach_to_partner = forms.ChoiceField(
    #     widget=RadioSelect,
    #     required=False,
    #     label="Which skill would you like to share with your partner?"
    # )

    # def __init__(self, *args, **kwargs):
    #     learn_choices = kwargs.pop('learn_from_partner')
    #     teach_choices = kwargs.pop('teach_to_partner')

    #     super().__init__(*args, **kwargs)

    #     self.fields['learn_from_partner'].choices = learn_choices
    #     self.fields['teach_to_partner'].choices = teach_choices

# from string import Template
# from django.utils.safestring import mark_safe

# class PictureWidget(forms.widgets.Widget):
#     def render(self, name, value, attrs=None):
#         html =  Template("""<img src="lore/media/$link"/>""")
#         return mark_safe(html.substitute(link=value))

class CredentialImageForm(forms.ModelForm):
    image = forms.ImageField(required=False, widget=FileInput)

    class Meta:
        model = CredentialImage
        fields = ['image', ]
        widgets = {
        'image': forms.FileInput()
        }


CredentialImageFormSet = inlineformset_factory(
    Profile,
    CredentialImage,
    widgets={'image': ImagePreviewWidget},
    fields=('image', ),
    extra=5,
    max_num=5,
)

# https://stackoverflow.com/questions/17021852/latitude-longitude-widget-for-pointfield/22309195#22309195
# http://django-map-widgets.readthedocs.io/en/latest/widgets/point_field_inline_map_widgets.html
# class LocationEntryForm(forms.ModelForm):

#     latitude = forms.FloatField(
#         min_value=-90,
#         max_value=90,
#         required=True,
#     )
#     longitude = forms.FloatField(
#         min_value=-180,
#         max_value=180,
#         required=True,
#     )

#     class Meta(object):
#         model = Profile
#         exclude = []
#         widgets = {'last_location': forms.HiddenInput()}

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         coordinates = self.initial.get('last_location', None)
#         if isinstance(coordinates, Point):
#             self.initial['latitude'], self.initial['longitude'] = coordinates.tuple

#     def clean(self):
#         data = super().clean()
#         latitude = data.get('latitude')
#         longitude = data.get('longitude')
#         point = data.get('last_location')
#         if latitude and longitude and not point:
#             data['last_location'] = Point(longitude, latitude)
#         return data
