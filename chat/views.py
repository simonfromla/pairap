from itertools import chain
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from user_profile.models import Profile
from .models import Pair


class MessageListView(LoginRequiredMixin, ListView):
    template_name = 'chat/listview.html'
    context_object_name = 'pair_list'

    def get_queryset(self, *args, **kwargs):
        current_user = Profile.objects.get(user__username=self.request.user)
        as_requester_list = Pair.objects.filter(
            requester=current_user,
            accepted=True,
            pending=False,
            denied=False
        )
        as_accepter_list = Pair.objects.filter(
            accepter=current_user,
            accepted=True,
            pending=False,
            denied=False
        )

        # Annotate each pair of the list with an "other_profile" to refer to either the A or R
        for pair in as_requester_list:
            pair.other_profile = pair.accepter
        for pair in as_accepter_list:
            pair.other_profile = pair.requester
        return list(chain(as_accepter_list, as_requester_list))
