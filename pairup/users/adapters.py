from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


# class UserAccountAdapter(DefaultAccountAdapter):

#     def save_user(self, request, user, form, commit=False):
#         """
#         This is called when saving user via allauth registration.
#         We override this to set additional data on user object.
#         """
#         # Do not persist the user yet so we pass commit=False
#         # (last argument)
#         user = super(UserAccountAdapter, self).save_user(request, user, form, commit=commit)
#         user.learn1 = form.cleaned_data.get('learn1')
#         # user.save()


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)
