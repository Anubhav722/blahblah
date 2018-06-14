from django import forms


class UrlPostForm(forms.Form):
    url = forms.URLField()


class UploadFileForm(forms.Form):
    file = forms.FileField()


class UploadResumeForm(forms.Form):
    file = forms.FileField()


class TrialUseCaseForm(UploadFileForm):
    email_address = forms.EmailField()


class SampleResumeForm(forms.Form):
    file = forms.CharField()
    skills = forms.CharField()
    email = forms.EmailField()
