from django.conf import settings
from django.contrib.gis.db import models
from django.urls import reverse
from django.db.models.signals import pre_delete, post_save
from django.dispatch.dispatcher import receiver

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from notifications.signals import notify


class ProfileManager(models.Manager):
    def all(self, *args, **kwargs):
        # Post.objects.all() = super(PostManager, self).all()
        return super(ProfileManager, self).filter(is_active=True)


def profile_photo_upload_loc(instance, filename):
        return "profile_photo/%s/%s" % (instance.user, filename)


def credential_photo_upload_loc(instance, filename):
        return "credential_photo/%s/%s" % (instance.profile, filename)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                null=True, blank=True, related_name='is_profile_to')
    # pairs = models.ManyToManyField('self', through='Pair',
    #                                symmetrical=False,
    #                                related_name='pair_to+')
    learn1 = models.CharField(max_length=54, blank=True, null=True,
                              verbose_name='Learn A')
    learn2 = models.CharField(max_length=54, blank=True, null=True,
                              verbose_name='Learn B')
    learn3 = models.CharField(max_length=54, blank=True, null=True,
                              verbose_name='Learn C')
    teach1 = models.CharField(max_length=54, blank=True, null=True,
                              verbose_name='Teach A')
    teach2 = models.CharField(max_length=54, blank=True, null=True,
                              verbose_name='Teach B')
    teach3 = models.CharField(max_length=54, blank=True, null=True,
                              verbose_name='Teach C')
    introduction = models.TextField(blank=True,
                                    null=True,
                                    verbose_name='Introduction',
                                    max_length=1000)

    profile_photo = models.ImageField(upload_to=profile_photo_upload_loc,
                                      blank=True,
                                      null=True,
                                      width_field='width_field',
                                      height_field='height_field',
                                      verbose_name='Profile Image',)
    profile_photo_thumbnail = ImageSpecField(source='profile_photo',
                                             processors=[ResizeToFill(40, 40)],
                                             format='PNG',
                                             options={'quality': 100})
    width_field = models.IntegerField(default=0, null=True)
    height_field = models.IntegerField(default=0, null=True)
    public = models.BooleanField(default=True, verbose_name='Public')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # latitude = models.
    last_location = models.PointField(null=True)

    objects = ProfileManager()

    class Meta:
        permissions = (
            ("can_edit_profile", "Can edit own profile"),
        )

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("profile:detail",
                       kwargs={"username": self.user})
    # @property
    def get_learn(self):
        list_of_learn = [self.learn1, self.learn2, self.learn3]
        return [field for field in list_of_learn if field]
    # @property
    def get_teach(self):
        list_of_teach = [self.teach1, self.teach2, self.teach3]
        return [field for field in list_of_teach if field]
        # return ((self.teach1, self.teach1),
        #         (self.teach2, self.teach2),
        #         (self.teach3, self.teach3))

    def add_relationship(self, person, learn, teach, pending=True, symm=True):
        # TODO: can lead to many same pairs. Altho with new prefs. Duplicate chat rooms
        pair = Pair.objects.create(
            requester=self,
            accepter=person,
            requester_learns=learn,
            requester_teaches=teach,
            pending=True)
        notify.send(
            self,
            recipient=person.user,
            verb='sent you a pairing request'
        )
        if symm:
            # avoid recursion by passing `symm=False`
            person.add_relationship(
                self,
                learn=learn,
                teach=teach,
                pending=True,
                symm=False)
        return pair

    def remove_relationship(self, person, pending=True, symm=True):
        # Opt for soft deletes
        pass
        # Pair.objects.filter(
        #     requester=self,
        #     accepter=person,
        #     pending=True).delete()
        if symm:
            # avoid recursion by passing `symm=False`
            person.remove_relationship(self, pending=True, symm=False)

    def is_pair(self, other):
        current_profile = self
        requesting_profile = Profile.objects.get(
            user__username=other)
        if Pair.objects.filter(requester=requesting_profile,
                               accepter=current_profile).exists():
            return True
        elif Pair.objects.filter(requester=current_profile,
                                 accepter=requesting_profile).exists():
            return True
        return False

    def is_accepted_pair(self, other):
        visitor = self
        current_profile = Profile.objects.get(
            user__username=other)
        if Pair.objects.filter(requester=visitor,
                               accepter=current_profile,
                               accepted=True).exists():
            return True
        elif Pair.objects.filter(requester=current_profile,
                                 accepter=visitor,
                                 accepted=True).exists():
            return True
        return False

    def is_denied_pair(self, other):
        visitor = self
        current_profile = Profile.objects.get(
            user__username=other)
        if Pair.objects.filter(requester=visitor,
                               accepter=current_profile,
                               denied=True).exists():
            return True
        elif Pair.objects.filter(requester=current_profile,
                                 accepter=visitor,
                                 denied=True).exists():
            return True
        return False

    def has_request_pending(self, other):
        visitor = self
        current_profile = Profile.objects.get(
            user__username=other)
        if current_profile.is_accepter.filter(
                accepter=current_profile,
                requester=visitor,
                pending=True).exists():
            return True
        return False

    def has_response_pending(self, other):
        visitor = self
        current_profile = Profile.objects.get(
            user__username=other)
        if current_profile.is_requester.filter(
                accepter=visitor,
                requester=current_profile,
                pending=True).exists():
            return True
        return False


# Create the user's profile upon creation of a User
def create_profile_receiver(sender, **kwargs):
    if kwargs['created']:
        Profile.objects.create(user=kwargs['instance'])


post_save.connect(create_profile_receiver, sender=settings.AUTH_USER_MODEL)


class CredentialImage(models.Model):
    profile = models.ForeignKey(
        Profile,
        default=None,
        related_name='credentialimage'
    )
    image = models.ImageField(
        upload_to=credential_photo_upload_loc,
        null=True,
        verbose_name='Image Credentials',
    )

    def __str__(self):
        return self.profile.user.username


# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=Profile)
def profile_photo_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.profile_photo:
        instance.profile_photo.file.delete(False)



@receiver(pre_delete, sender=CredentialImage)
def credential_photo_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    # TODO: instance..cred related name fix
    if instance:
        instance.image.delete(False)


class Changelog(models.Model):
    log_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(Profile, related_name='changelog')
    log_preference = models.CharField(max_length=400)

    def __str__(self):
        return self.owner.user.username


class Pair(models.Model):

    requester = models.ForeignKey(Profile, related_name='is_requester')
    accepter = models.ForeignKey(Profile, related_name='is_accepter')

    requester_learns = models.CharField(max_length=60, null=True)
    requester_teaches = models.CharField(max_length=60, null=True)

    pending = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    denied = models.BooleanField(default=False)

    completed = models.BooleanField(default=False)

    staff_only = models.BooleanField(default=False)

    class Meta():
        unique_together = ('requester', 'accepter')

    def __str__(self):
        return str(self.pk)

    # def with_requester_being(self, other):
    #     current_profile = self
    #     requester = Profile.objects.get(
    #         user=other)
    #     if requester.is_requester.filter(
    #             accepter=current_profile,
    #             requester=requester,
    #             pending=True).exists():
    #         return True
    #     return False

    # def with_accepter_being(self, other):
    #     current_profile = self
    #     accepter = Profile.objects.get(
    #         user__username=other)
    #     if accepter.is_accepter.filter(
    #             accepter=accepter,
    #             requester=current_profile,
    #             pending=True).exists():
    #         return True
    #     return False
