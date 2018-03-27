from django.contrib import admin
from .models import Profile, Pair
# from .forms import LocationEntryForm


# class LocationEntryAdmin(admin.ModelAdmin):
#     form = LocationEntryForm

# admin.site.register(Profile, LocationEntryAdmin)


class RelationshipInline(admin.StackedInline):
    # Need /admin/user_profile/profile/{id}/change/ to include all
    # pairs. Currently only showing instances in which user is 'requester'
    model = Pair
    fk_name = 'requester'


class ProfileModelAdmin(admin.ModelAdmin):
    inlines = [RelationshipInline]
    list_display = ['user', 'public', 'updated']
    list_filter = ['updated', 'timestamp']

    fieldsets = (
        (None, {'fields': ('user', )}),
        ('Skill set', {
            'fields': (
                'learn1', 'learn2', 'learn3', 'teach1',
                'teach2', 'teach3', 'last_location'
            )
        }),
        ("Public", {'fields': ('public', )}),
    )

    ordering = ('-updated',)

    class Meta:
        model = Profile


admin.site.register(
    Pair,
    list_display=[
        "id", "requester", "accepter", "pending",
        "accepted", "denied", "requester_learns",
        "requester_teaches"
    ],
    list_display_links=[
        "requester", "accepter"
    ],
)


admin.site.register(Profile, ProfileModelAdmin)
