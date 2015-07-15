from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    # Additional information about User
    full_name = models.CharField(max_length=255, blank=True) # フルネーム
    full_name_transcription = models.CharField(max_length=255, blank=True) # フルネームヨミ
    card_number = models.CharField(max_length=255, blank=True)  # 利用券番号

def create_user_profile(sender, instance, created, **kwargs):
    """
    if user is created (or changed),
    then create user profile about the user, using signal

    kwargs contains such key 'raw', 'signal', 'using'
    """

    if created:
        # user is created, not changed
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

