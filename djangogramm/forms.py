from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django import forms
import re
import os

from .models import User, Post, Media, Tag

NO_USER_AVATAR = os.getenv('NO_USER_AVATAR')


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label='',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'


class EditProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('avatar', 'bio', 'full_name')

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs['class'] = 'form-control'
        self.fields['full_name'].widget.attrs['class'] = 'form-control'
        self.fields['bio'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'aria-label': 'With textarea',
        })


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'aria-label': 'With textarea',
            'maxlength': 255,
            'style': 'height: 170px;',
        })

    user = forms.HiddenInput()


class MediaForm(forms.Form):
    image = forms.FileField(required=True)
    image2 = forms.FileField(required=False)
    image3 = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super(MediaForm, self).__init__(*args, **kwargs)

        self.fields['image'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['image2'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['image3'].widget.attrs.update({'class': 'form-control form-control-sm'})


def validate_tag(value):
    pattern = r'^#[A-Za-z]+$'
    tags = re.findall(r'#\w+', value)

    if ' ' in value:
        raise ValidationError('Tags should not contain spaces.')

    for tag in tags:
        if not re.match(pattern, tag):
            raise ValidationError('Tags should start with "#" and contain only Latin letters.')


class EditPostForm(forms.Form):
    description = forms.CharField(max_length=255, validators=[MaxLengthValidator(255)])
    tags = forms.CharField(max_length=100, validators=[validate_tag])

    def __init__(self, *args, **kwargs):
        super(EditPostForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'aria-label': 'With textarea',
            'max-length': '255',
            'style': 'height: 100px;'
        })
        self.fields['tags'].widget.attrs.update({'class': 'form-control'})


class SendEmailForm(forms.Form):
    email = forms.EmailField(max_length=100)


class TagForm(forms.Form):
    tags = forms.CharField(max_length=100, validators=[validate_tag])

    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)

        # self.fields['tags'].widget.attrs.update({'class': 'form-control',
        #                                          'maxlenght': 100,
        #                                          'style': 'height: 100px;',
        #                                          'aria-label': 'With textarea',
        #                                          })
        self.fields['tags'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'aria-label': 'With textarea',
            'maxlength': 100,
            'style': 'height: 70px;',
        })
        self.fields['tags'].help_text = 'Define tags in a row like #mytag#anothertag'


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
