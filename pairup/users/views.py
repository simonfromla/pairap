from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import ListView, RedirectView, UpdateView
from django.shortcuts import render_to_response
from django.template import RequestContext

from allauth.account.forms import AddEmailForm, ChangePasswordForm
# from allauth.account.views import SignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
# from .forms import initialPreferenceForm

# class MySignupView(SignupView):
#     initial_preference_form = initialPreferenceForm

#     def get_context_data(self, *args, **kwargs):
#         # Pass the extra form to this view's context
#         context = super(
#             MySignupView, self).get_context_data(*args, **kwargs)
#         context['initial_preference_form'] = initialPreferenceForm
#         return context

#     def form_valid(self, form):
#         self.user = form.save(self.request)
#         return super(MySignupView, self).form_valid(form)
# class MyEmailPasswordView(LoginRequiredMixin, EmailView):
#     template_name = 'account/joint_email_pass.html'
#     form_class = AddEmailForm
#     change_password_form = ChangePasswordForm
#     success_url = reverse_lazy('change_email_pass')

#     def __init__(self, *args, **kwargs):
#         super(MyEmailPasswordView, self).__init__(**kwargs)

#     def get_success_url(self):
#         return reverse('change_email_pass')

#     def get_context_data(self, *args, **kwargs):
#         # Pass the extra form to this view's context
#         context = super(
#             MyEmailPasswordView, self).get_context_data(*args, **kwargs)
#         context['change_password_form'] = ChangePasswordForm
#         # V2! -- need to change success url?
#         # redirect back to joint form view instead of single form view
#         # Try subclassing AllAuth's views and changin the success urls?
#         # print(self.get_success_url())
#         # print(super(MyEmailPasswordView, self).get_success_url())
#         return context


# class UserDetailView(LoginRequiredMixin, DetailView):
#     model = User
#     # These next two lines tell the view to index lookups by username
#     slug_field = 'username'
#     slug_url_kwarg = 'username'

# for custom 404.
# def handler404(request):
#     response = render_to_response('404.html', {},
#                                   context_instance=RequestContext(request))
#     response.status_code = 404
#     return response


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        # return reverse('users:detail',
                       # kwargs={'username': self.request.user.username})
        return reverse('users:update')


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['is_active']
    template_name = 'account/joint_email_pass.html'
    add_email_form = AddEmailForm
    change_password_form = ChangePasswordForm
    success_url = reverse_lazy('change_email_pass')

    # def __init__(self, *args, **kwargs):
    #     super(MyEmailPasswordView, self).__init__(**kwargs)

    def get_context_data(self, *args, **kwargs):
        # Pass the extra form to this view's context
        context = super(
            UserUpdateView, self).get_context_data(*args, **kwargs)
        context['change_password_form'] = ChangePasswordForm
        context['add_email_form'] = AddEmailForm
        # V2! -- need to change success url?
        # redirect back to joint form view instead of single form view
        # Try subclassing AllAuth's views and changin the success urls?
        # print(self.get_success_url())
        # print(super(MyEmailPasswordView, self).get_success_url())
        return context
    # we already imported User in the view code above, remember?
    # model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:update')

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)
