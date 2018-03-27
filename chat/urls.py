from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^$',
        view=views.MessageListView.as_view(),
        name='list'
    ),
    # url(
    #     regex=r'^(?P<username>[\w.@+-]+)/$',
    #     view=views.ProfileDetailView.as_view(),
    #     name='detail'
    # ),

]
