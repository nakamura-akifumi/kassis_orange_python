from django import forms
from django.core.validators import RegexValidator
from django.core.validators import EmailValidator

class UserForm(forms.Form):
    CounterBucketName = "users"

    # https://docs.djangoproject.com/en/1.8/ref/forms/fields/

    user_id = forms.CharField(min_length=1, max_length=64, required=True,
        validators=[
        RegexValidator(
            regex='^[a-zA-Z0-9]*$',
            message='ユーザ名は半角英数のみです。',
            code='invalid_user_id'
        ),
    ])
    full_name = forms.CharField(min_length=1, max_length=128, required=False)
    full_name_transcription = forms.CharField(min_length=1, max_length=128, required=False)

    email = forms.EmailField(required=False, validators=[EmailValidator])
    user_number = forms.CharField(required=False,
        validators=[
        RegexValidator(
            regex='^[a-zA-Z0-9]*$',
            message='利用者番号は、半角英数のみです。',
            code='invalid_usernumber'
        ),
    ])
    phone_number = forms.CharField(required=False,
        validators=[
        RegexValidator(
            regex='^[0-9\-]*$',
            message='電話番号は半角数字とハイフンのみです。',
            code='invalid_phonenumber'
        ),
    ])

    #password = forms.CharField(widget=forms.PasswordInput(), min_length=8)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

