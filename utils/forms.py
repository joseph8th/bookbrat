from django.forms import ModelForm

class RequestModelForm(ModelForm):
    """
    Sub-class ModelForm providing instance of request and save
    with appropriate user.
    """
    def __init__(self, request, *args, **kwargs):
        """ Override init to grab request object. """
        self.request = request
        super(RequestModelForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        mf = super(RequestModelForm, self).save(commit=False)
#        mf.owner = self.request.user
        if commit:
            mf.save()
        return mf
