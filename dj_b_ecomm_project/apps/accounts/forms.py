# Import Django form utilities
from django import forms

# Import built-in authentication forms and models
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# Import your custom user model
from apps.accounts.models import CustomUser
from django.utils.translation import gettext_lazy as _

# -------------------------------------------------
# User Registration Form
# -------------------------------------------------
class UserRegistrationForm(UserCreationForm):
    """
    A custom registration form that extends Django's built-in UserCreationForm.
    Adds an email field and an optional profile image upload.
    """

    email = forms.EmailField(
        required=True,
        label=_("Email"),
        help_text=_("Enter a valid email address."),
        widget=forms.EmailInput()
    )

    profile_image = forms.ImageField(
        required=False,
        label=_("Profile Image"),
        help_text=_("Optional: Upload a profile image.")
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2", "profile_image"]
        labels = {
            "username": _("Username"),
            "email": _("Email"),
            "password1": _("Password"),
            "password2": _("Confirm Password"),
            "profile_image": _("Profile Image"),
        }
        help_texts = {
            "username": _("Choose a unique username."),
            "password1": _("Your password must contain at least 8 characters."),
            "password2": _("Enter the same password again for confirmation."),
        }
        widgets = {
            "username": forms.TextInput(),
            "password1": forms.PasswordInput(attrs={'placeholder': _("Enter your password")}),
            "password2": forms.PasswordInput(attrs={'placeholder': _("Confirm your password")}),
        }

    def save(self, commit=True):
        """
        Save the user instance with additional fields.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        image = self.cleaned_data.get('profile_image')

        if image:
            user.profile_image = image

        if commit:
            user.save()

        return user


# -------------------------------------------------
# User Login Form
# -------------------------------------------------

class UserLoginForm(AuthenticationForm):
    """
    A custom login form that uses email instead of username for authentication.
    """

    username = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput()
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput()
    )
