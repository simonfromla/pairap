from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import (
    Http404,
    get_object_or_404,
    redirect,
    reverse,
)
from django.views.generic import (
    DetailView,
    UpdateView,
    FormView,
    TemplateView,
    View
)
from .models import Profile
from chat.models import Chat
from chat.models import Pair
from .forms import (
    PreferenceUpdateForm,
    ProfileUpdateForm,
    CredentialImageFormSet,
    PairRequestForm,
    PublicToggleForm,
)
from .mixins import AjaxFormMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from user_profile.permissions import has_perm_or_is_owner


# Create your views here.


# class ProfilePublicAjaxView(View):
#     def post(self, request, *args, **kwargs):
#         print("ONE")
#         if self.request.is_ajax():
#             public = self.request.GET.get('t_or_f')

#             if self.request.user.is_authenticated:
#                 user = self.request.user
#                 # Profile.objects.filter(user=user).update(last_location=Point((lat, lon)))
#                 p = Profile.objects.get(user=user)
#                 setattr(p, 'last_location', Point(lon, lat, srid=4326))
#                 p.save()

#             return JsonResponse({'key': "value"}, safe=False)


class PublicToggleFormView(AjaxFormMixin, FormView):
    form_class = PublicToggleForm
    success_url = '/form-success/'
    template_name = 'user_profile/profile_detail.html'

    def get_form_kwargs(self):
        kwargs = super(PublicToggleFormView, self).get_form_kwargs()
        profile = Profile.objects.get(user=self.request.user)
        kwargs.update({'instance': profile})
        return kwargs


class CheckPublicAjaxView(View):

    def post(self, request):
        if self.request.is_ajax():
            # TODO: error message
            # PERMISSION-TO-CLICK-LINK CHECKS HERE
            if self.request.user.is_authenticated():
                if self.request.user.is_profile_to.public:
                    data = {
                        'message': "Allow button click?"
                    }
                    # custom permission checks
                    return JsonResponse(data)
                else:
                    data = {
                        'error': "ERRO HERE",
                        'message': "EORR MESG"
                    }
                    return JsonResponse(data, status=400)
            else:
                data = {
                    'message': "Log in to get started!"
                }
                return JsonResponse(data, status=400)


class ProfileDetailView(DetailView):
    template_name = 'user_profile/profile_detail.html'

    def is_pair(self, **kwargs):
        # Method for the template to check whether the request.user &
        # current profile object have a pair relationship.
        # Does not determine which user is R & A
        current_profile = self.get_object()
        requesting_profile = Profile.objects.get(
            user__username=self.request.user)
        if Pair.objects.filter(requester=requesting_profile,
                               accepter=current_profile).exists():
            return True
        elif Pair.objects.filter(requester=current_profile,
                                 accepter=requesting_profile).exists():
            return True
        return False

    def pending_to_requester(self, **kwargs):
        # Method for the template to determine which CTA button to display.
        # Differentiates profiles btwn R & A
        current_profile = self.get_object()
        requester = Profile.objects.get(
            user__username=self.request.user)
        if requester.is_requester.filter(
                accepter=current_profile,
                requester=requester,
                pending=True).exists():
            return True
        return False

    def pending_to_accepter(self, **kwargs):
        current_profile = self.get_object()
        accepter = Profile.objects.get(
            user__username=self.request.user)
        if accepter.is_accepter.filter(
                accepter=accepter,
                requester=current_profile,
                pending=True).exists():
            return True
        return False

    def accepted_pair(self, **kwargs):
        pass

    def get_object(self, *args, **kwargs):
        username = self.kwargs.get('username')
        if username is None:
            raise Http404
        obj = get_object_or_404(Profile, user__username__iexact=username)
        return obj

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            visitor = Profile.objects.get(
                user=self.request.user)
            current_profile = self.get_object()
            context['public_toggle_form'] = PublicToggleForm(
                instance=current_profile
            )
            context['is_pair'] = visitor.is_pair(
                current_profile)
            context['visitor_has_request_pending'] = visitor.has_request_pending(
                current_profile)
            context['visitor_has_response_pending'] = visitor.has_response_pending(
                current_profile)
            context['is_denied_pair'] = visitor.is_denied_pair(
                current_profile)
            context['is_accepted_pair'] = visitor.is_accepted_pair(
                current_profile)
        return context


class PreferenceUpdateView(LoginRequiredMixin, UpdateView):
    # permission_required = ('user_profile.change_profile')
    form_class = PreferenceUpdateForm
    model = Profile
    template_name = 'user_profile/preference_edit.html'
    raise_exception = True

    # def test_func(self):

    def get_object(self, *args, **kwargs):
        user_profile = self.kwargs.get('username')
        obj = get_object_or_404(Profile, user__username=user_profile)
        can_edit = has_perm_or_is_owner(
            self.request.user,
            'user_profile.change_profile',
            instance=obj,
        )
        if not can_edit:
            raise Http404
        return obj

    def form_valid(self, form):
        # instance = form.save(commit=False)
        # if no edits, dont save
        # form.instance.user = self.request.user
        # print(form.instance)
        return super(PreferenceUpdateView, self).form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUpdateForm
    template_name = 'user_profile/profile_edit.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        data = super(ProfileUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['credential_image'] = CredentialImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['credential_image'] = CredentialImageFormSet(
                instance=self.object)
        return data

    def get_object(self, *args, **kwargs):
        user_profile = self.kwargs.get('username')
        obj = get_object_or_404(Profile, user__username=user_profile)
        can_edit = has_perm_or_is_owner(
            self.request.user,
            'user_profile.change_profile',
            instance=obj,
        )
        if not can_edit:
            raise Http404
        return obj

    def form_valid(self, form):
        data = self.get_context_data()
        formset = data['credential_image']
        if formset.is_valid():
            print("1", formset)
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.object.get_absolute_url())
        else:
            print("WTF")

        instance = form.save(commit=False)
        instance.user = self.request.user
        return super(ProfileUpdateView, self).form_valid(form)


class PairRequestView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = PairRequestForm
    template_name = 'user_profile/pair_request.html'
    raise_exception = True

    def test_func(self):
        # Test that viewers of this page have public as True. The recipients must also be True
        # cannot request with yourself.
        # Cannot request with someone who has denied you
        responding_profile = Profile.objects.get(
            user__username=self.request.user)
        requesting_profile = Profile.objects.get(
            user__username=self.kwargs['username'])
        if not responding_profile == requesting_profile:
            if responding_profile.public is True and requesting_profile.public is True:
                return True
        return False

    def get_success_url(self, **kwargs):
        return reverse('profile:detail', args=[self.kwargs['username']])

    def get_context_data(self, **kwargs):
        # Get username from kwargs to add context to the pair request page
        context = super(PairRequestView, self).get_context_data(**kwargs)
        context['request_to_user'] = self.kwargs.get('username')
        return context

    def get_form_kwargs(self, *args, **kwargs):
        requester_obj = Profile.objects.get(
            user__username=self.request.user)
        accepter_obj = Profile.objects.get(
            user__username=self.kwargs.get('username'))

        what_will_you_teach_set = requester_obj.get_teach()
        what_will_you_learn_set = accepter_obj.get_teach()

        kwargs = super().get_form_kwargs()

        # Pass additional kwargs to the form
        kwargs['learn_from_partner'] = what_will_you_learn_set
        kwargs['teach_to_partner'] = what_will_you_teach_set

        return kwargs

    def form_valid(self, form):
        super(PairRequestView, self).form_valid(form)

        learn = form.cleaned_data['learn_from_partner']
        teach = form.cleaned_data['teach_to_partner']

        accepter = Profile.objects.get(user__username=self.kwargs["username"])
        requester = Profile.objects.get(user__username=self.request.user)

        # add learn and teach, other data to the new relationship
        requester.add_relationship(accepter, learn=learn, teach=teach, symm=False)

        return super(PairRequestView, self).form_valid(form)


class PairResponseView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'user_profile/pair_response.html'
    raise_exception = True  # Issue 403

    def test_func(self):
        # Test that viewers of this page have the appropriate pair object, and are pending
        responding_profile = Profile.objects.get(
            user__username=self.request.user)
        requesting_profile = Profile.objects.get(
            user__username=self.kwargs['username'])
        if Pair.objects.filter(requester=requesting_profile,
                               accepter=responding_profile,
                               pending=True).exists():
            return True
        return False

    def get_context_data(self, **kwargs):
        # Get username from kwargs to add context to the pair request page
        context = super(PairResponseView, self).get_context_data(**kwargs)
        context['respond_to_user'] = self.kwargs.get('username')
        responding_profile = Profile.objects.get(
            user__username=self.request.user)
        requesting_profile = Profile.objects.get(
            user__username=self.kwargs['username'])

        pair_object = Pair.objects.get(requester=requesting_profile, accepter=responding_profile)
        # TODO: why is None allowed here? Trace to roots. Remove.
        context['requester_learns'] = pair_object.requester_learns
        context['requester_teaches'] = pair_object.requester_teaches
        return context

    def post(self, request, *args, **kwargs):
        if 'accept' in self.request.POST:
            responding_profile = Profile.objects.get(
                user__username=self.request.user)
            requesting_profile = Profile.objects.get(
                user__username=self.kwargs['username'])
            pair_object = Pair.objects.get(requester=requesting_profile, accepter=responding_profile)
            pair_object.pending = False
            pair_object.accepted = True
            pair_object.save()
            Chat.objects.create(pair=pair_object)
            return redirect('message:list')
        else:
            responding_profile = Profile.objects.get(
                user__username=self.request.user)
            requesting_profile = Profile.objects.get(
                user__username=self.kwargs['username'])
            pair_object = Pair.objects.get(requester=requesting_profile, accepter=responding_profile)
            pair_object.denied = True
            pair_object.pending = False
            pair_object.save()
            # allow for re-offer?
            return redirect(requesting_profile.get_absolute_url())
