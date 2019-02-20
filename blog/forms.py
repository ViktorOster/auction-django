from django import forms

from .models import Post, Bid
from datetime import datetime, timedelta
from django.utils import timezone

from django.forms import EmailField

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


class BidForm(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ('bid',)

    def __init__(self, post, user, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        self.post = post
        self.user = user

    def clean_bid(self):
        bid = self.cleaned_data['bid']
        bid = float("{0:.2f}".format(float(bid)))
        price = float("{0:.2f}".format(float(self.post.price)))

        highestBid = Bid.objects.filter(
            post=self.post, bid=float(self.post.price)).first()

        if highestBid != None:
            if highestBid.author == self.user:
                raise forms.ValidationError(
                    'You are already winning on the auction')

        if self.post.author == self.user:
            raise forms.ValidationError('Cannot bid on own auction!')

        if float(bid) <= float(price) + 0.009:
            raise forms.ValidationError(
                'Bid must be higher than current price')
        return bid

    def save(self, commit=True):
        bidToSave = super(BidForm, self).save(commit=False)
        bidToSave.bid = self.cleaned_data["bid"]
        bidToSave.post = self.post
        bidToSave.author = self.user
        postOriginal = Post.objects.get(pk=self.post.pk)
        postOriginal.price = self.cleaned_data["bid"]
        postOriginal.save()
        # print(postOriginal.title)
        self.post.price = self.cleaned_data["bid"]

        if commit:
            bidToSave.save()
        return bidToSave


class EditUserForm(forms.ModelForm):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.passwordIsEmpty = False
        super(EditUserForm, self).__init__(*args, **kwargs)
        #self.fields['new_password1'].initial = self.user.password
        #self.fields['new_password2'].initial = self.user.password
        self.fields['new_email'].initial = self.user.email

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    new_email = EmailField(label=_("New email address"), required=False)

    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput(render_value=True), required=False)
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput(render_value=True), required=False)

    class Meta:
        model = User
        # Add all the fields you want a user to change
        fields = ('new_email', 'new_password1', 'new_password2')

    def clean_new_password2(self):
        #print("CLEANING PASSWORD")

        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 == "" and password2 == "":
            self.passwordIsEmpty = True
            return
        else:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )

        return password2

    def save(self, commit=True):

        if self.passwordIsEmpty == False:
            self.user.set_password(self.cleaned_data['new_password1'])

        self.user.email = self.cleaned_data['new_email']

        if commit:
            self.user.save()
            #print("SAVED PASSWORD")
        return self.user


class UserCreationForm(UserCreationForm):
    email = EmailField(label=_("Email address"), required=True,
                       help_text=_("Required."))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class PostForm(forms.ModelForm):
    deadline_date = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M'])

    class Meta:
        model = Post
        fields = ('title', 'text', 'price', 'deadline_date')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.css_class = "rule"
        self.fields['title'].label = _('Title')
        self.fields['title'].label_suffix = ""

        self.fields['text'].label = _('Description')
        self.fields['text'].label_suffix = ""

        self.fields['price'].label = _('Price')
        self.fields['price'].label_suffix = ""

        self.fields['deadline_date'].label = _(
            'Deadline (format: YYYY-MM-DD HH:MM)')
        self.fields['deadline_date'].label_suffix = ""

    def clean_deadline_date(self):
        my_date = self.cleaned_data['deadline_date']
        three_days_from_now = timezone.now() + timedelta(hours=72)
        format(three_days_from_now, '%Y-%m-%d %H:%M')
        if my_date < three_days_from_now:
            raise forms.ValidationError(
                'Minimum deadline is 72h from current time')
        return my_date


class ConfPost(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
