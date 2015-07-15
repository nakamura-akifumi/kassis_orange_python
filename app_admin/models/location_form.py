from django import forms

class LocationForm(forms.Form):
    # https://docs.djangoproject.com/en/1.8/ref/forms/fields/

    location_id = forms.CharField(required=True)
    name = forms.CharField(required=False)
    note = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)

