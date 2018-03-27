from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^public_toggle$',
        view=views.PublicToggleFormView.as_view(),
        name='public_toggle'
    ),
    url(
        regex=r'^check_public$',
        view=views.CheckPublicAjaxView.as_view(),
        name='check_public'
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/$',
        view=views.ProfileDetailView.as_view(),
        name='detail'
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/edit_preference/$',
        view=views.PreferenceUpdateView.as_view(),
        name='edit_preference'
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/edit_profile/$',
        view=views.ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/pair_request/$',
        view=views.PairRequestView.as_view(),
        name='pair_request'
    ),
    url(
        regex=r'^(?P<username>[\w.@+-]+)/pair_response/$',
        view=views.PairResponseView.as_view(),
        name='pair_response'
    ),
]
