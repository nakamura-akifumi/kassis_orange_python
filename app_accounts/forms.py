from django.contrib.auth.models import User
from django.forms import ModelForm
from app_accounts.models import UserProfile

class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ['date_joined']

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user']
        #fields = "__all__"
