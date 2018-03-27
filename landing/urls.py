from django.conf.urls import url
from . import views


urlpatterns = [
    url(
        regex=r'^$',
        view=views.HomeListView.as_view(template_name='landing/home.html'),
        name='home'
    ),
    url(
        regex=r'^ajax/landing_location/$',
        view=views.HomeLocationAjaxView.as_view(),
        name='home_location'
    ),
    # url(
    #     regex=r'^s*',
    #     view=views.NotificationsView.as_view(),
    # ),
    # url(
    #     '^inbox/notifications/',
    #     include(notifications.urls, namespace='notifications')
    # ),
]
