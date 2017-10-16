from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile, Site
from rss.models import Article

# class RegisterForm(UserCreationForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs['class'] = 'form-control'
#         self.fields['password1'].widget.attrs['class'] = 'form-control'
#         self.fields['password2'].widget.attrs['class'] = 'form-control'


# class LoginForm(AuthenticationForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs['class'] = 'form-control'
#         self.fields['password'].widget.attrs['class'] = 'form-control'

class UserCreateForm(UserCreationForm):
    pass


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = (
            'plan',
        )


class SiteForm(forms.ModelForm):

    class Meta:
        model = Site
        fields = (
            "name", "url"
        )


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = (
            "title", "url"
        )
