# Used in PreferenceUpdateView & ProfileUpdateView for profile editing
# permission check
def has_perm_or_is_owner(user_object,
                         permission,
                         instance=None):
    if instance is not None:
        if user_object == instance.user:
            return True
    return user_object.has_perm(
        permission
    )
