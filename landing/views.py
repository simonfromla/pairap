from django.views.generic import ListView, View
from django.http import JsonResponse
from django.db.models import Q
from functools import reduce
import operator
from django.contrib.gis.geos import Point

from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from user_profile.models import Profile
# Create your views here.
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt


# class NotificationsView(View):
#     def get(self, request, *args, **kwargs):
#         profile = Profile.objects.get(user__username=self.request.user)
#         notifs = profile.user.notifications.unread()
#         # print(notifs)
#         return render(request, 'base.html', {'notifs': notifs})


class HomeLocationAjaxView(View):
    def get(self, request, *args, **kwargs):
        if self.request.is_ajax():
            lat = self.request.GET.get('lat')
            # lat = self.request.GET.get('lat', 'provide Seoul default?')
            lon = self.request.GET.get('lon')
            lat = float(lat)
            lon = float(lon)

            round(lat, 4)
            round(lon, 4)

            if self.request.user.is_authenticated:
                user = self.request.user
                # Profile.objects.filter(user=user).update(last_location=Point((lat, lon)))
                p = Profile.objects.get(user=user)
                setattr(p, 'last_location', Point(lon, lat, srid=4326))
                p.save()

            return JsonResponse({'key': "value"}, safe=False)


class HomeListView(ListView):
    model = Profile
    context_object_name = 'all_user_posts'
    paginate_by = 2

    queryset = Profile.objects.filter(public=True).order_by('-created')
    # TODO CLEAN UP and combine views -- see: PSEUDO on trello
    # def get_queryset(self):
    #     # return Profile.objects.filter(public=True).order_by('-created')
    #     return Profile.objects.filter(public=True)

    # def get_context_data(self, *args, **kwargs):
    #     query = self.request.GET.get('q')
    #     qs = Profile.objects.all()
    #     if query:
    #         qs = qs.filter(introduction__icontains=query)

    def get_queryset(self):
        result = super(HomeListView, self).get_queryset()

        # Search functions
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(learn1__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(learn2__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(introduction__icontains=q) for q in query_list))
            )
        else:
            # At least one pref filled out, location HAS been shared once.
            # TODO: incorporate those who havent shared location with a general location
            if self.request.user.is_authenticated:
                current_user = Profile.objects.get(user=self.request.user)
                if current_user.last_location:
                    user_list = Profile.objects.annotate(
                        distance_away=Distance(
                            'last_location', current_user.last_location
                        )).filter(
                        Q(learn1__isnull=False) | Q(learn2__isnull=False) |
                        Q(learn3__isnull=False) | Q(teach1__isnull=False) |
                        Q(teach2__isnull=False) | Q(teach3__isnull=False),
                        public=True,
                        last_location__distance_lte=(
                            current_user.last_location, D(km=500)))
                    # TODO Order closest to farthest
                    # paginate
                    result = user_list
        return result
