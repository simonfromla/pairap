# from allauth.socialaccount.forms import SignupForm
# from allauth.account.forms import SetPasswordField, PasswordField
# from allauth.account import app_settings
# from allauth.account.utils import user_field, user_email, user_username
from django.utils.translation import ugettext_lazy as _
from django import forms
# from django.forms import forms
# from allauth.account.forms import BaseSignupForm
from user_profile.models import Profile


# Don't opt for password setting with social login. Defeats the point of social login.
# https://stackoverflow.com/questions/47121638/how-to-set-password-in-user-table-when-user-is-signup-using-google-or-facebook-d
# class SocialPasswordedSignupForm(BaseSignupForm):

#     password1 = SetPasswordField(label=_("Password"))
#     password2 = SetPasswordField(label=_("Confirm Password"))

#     def __init__(self, *args, **kwargs):
#         self.sociallogin = kwargs.pop('sociallogin')
#         user = self.sociallogin.user
#         # TODO: Should become more generic, not listing
#         # a few fixed properties.
#         initial = {'email': user_email(user) or '',
#                    'username': user_username(user) or '',
#                    'first_name': user_field(user, 'first_name') or '',
#                    'last_name': user_field(user, 'last_name') or ''}
#         kwargs.update({
#             'initial': initial,
#             'email_required': kwargs.get('email_required',
#                                          app_settings.EMAIL_REQUIRED)})
#         super(SocialPasswordedSignupForm, self).__init__(*args, **kwargs)

#     def save(self, request):
#         adapter = get_adapter()
#         user = adapter.save_user(request, self.sociallogin, form=self)
#         self.custom_signup(request, user)
#         return user

#     def clean(self):
#         super(SocialPasswordedSignupForm, self).clean()
#         if "password1" in self.cleaned_data \
#                 and "password2" in self.cleaned_data:
#             if self.cleaned_data["password1"] \
#                     != self.cleaned_data["password2"]:
#                 raise forms.ValidationError(_("You must type the same password"
#                                               " each time."))

#     def raise_duplicate_email_error(self):
#         raise forms.ValidationError(
#             _("An account already exists with this e-mail address."
#               " Please sign in to that account first, then connect"
#               " your %s account.")
#             % self.sociallogin.account.get_provider().name)

#     def custom_signup(self, request, user):
#         password = self.cleaned_data['password1']
#         user.set_password(password)
#         user.save()


# class SocialPasswordedSignupForm(SignupForm):

#     password1 = SetPasswordField(max_length=128,label=("Password"))
#     password2 = PasswordField(max_length=128, label=("Password (again)"))

# #taken from https://github.com/pennersr/django-allauth/blob/master/allauth/account/forms.py

#     def clean_password2(self):
#         if ("password1" in self.cleaned_data and "password2" in self.cleaned_data):
#             if (self.cleaned_data["password1"] != self.cleaned_data["password2"]):
#                 raise forms.ValidationError(("Your passwords do not match"))
#         return self.cleaned_data["password2"]

#     def signup(self, request, user):
#         user.set_password(self.user, self.cleaned_data["password1"])
#         user.save()


class SignupForm(forms.Form):

    learn1 = forms.CharField(max_length=50, label='Learn', required=False)
    teach1 = forms.CharField(max_length=50, label='Teach', required=False)

    class Meta:
        model = Profile

    def clean(self):
        cleaned_data = super().clean()
        if not self.cleaned_data['learn1'] or self.cleaned_data['teach1']:
            raise forms.ValidationError("Specify at least one skill you can teach or would like to learn")
        else:
            return cleaned_data

    def save(self, user):
        # if not self.cleaned_data['learn1'] or self.cleaned_data['teach1']:
        #     raise forms.ValidationError("Specify at least one")
        user.is_profile_to.learn1 = self.cleaned_data['learn1']
        user.is_profile_to.teach1 = self.cleaned_data['teach1']
        user.save()
        user.is_profile_to.save()
