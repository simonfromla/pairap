def prefs_are_none(profile):
    none = True
    if profile.get_teach() or profile.get_learn():
        none = False
    return none
