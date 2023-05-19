from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User, Post, Media, Tag
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
import re


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label='',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'avatar')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # self.fields['avatar'].widget.attrs.update({'class': 'form-control'})

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields[
            'username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields[
            'password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields[
            'password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'aria-label': 'With textarea'
        })

    user = forms.HiddenInput()


class MediaForm(forms.Form):
    image = forms.FileField(required=True)
    image2 = forms.FileField(required=False)
    image3 = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super(MediaForm, self).__init__(*args, **kwargs)

        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['image2'].widget.attrs.update({'class': 'form-control'})
        self.fields['image3'].widget.attrs.update({'class': 'form-control'})


def validate_tag(value):
    pattern = r'^#[A-Za-z]+$'
    tags = re.findall(r'#\w+', value)

    if ' ' in value:
        raise ValidationError('Tags should not contain spaces.')

    for tag in tags:
        if not re.match(pattern, tag):
            raise ValidationError('Tags should start with "#" and contain only Latin letters.')


class TagForm(forms.Form):
    tags = forms.CharField(max_length=100, validators=[validate_tag])

    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)

        self.fields['tags'].widget.attrs.update({'class': 'form-control'})
        self.fields[
            'tags'].help_text = '<span class="form-text">Define tags in a row like #mytag#anothertag</span>'


class CommentForm(forms.Form):
    text = forms.CharField(max_length=255, validators=[MaxLengthValidator(255)])

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

        self.fields['text'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'aria-label': 'With textarea',
            'max-length': '255',
            'style': 'height: 100px;'
        })


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login')
    password = forms.PasswordInput()

    def __init__(self, *args, **kwargs):
        super(LoginUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'
