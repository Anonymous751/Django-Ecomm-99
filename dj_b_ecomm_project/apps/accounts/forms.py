# Import Django form utilities
from django import forms

# Import built-in authentication forms and models
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# Import your custom user model
from apps.accounts.models import CustomUser


# -------------------------------------------------
# User Registration Form
# -------------------------------------------------
class UserRegistrationForm(UserCreationForm):
    """
    A custom registration form that extends Django's built-in UserCreationForm.
    Adds an email field and an optional profile image upload.
    """

    email = forms.EmailField(required=True, help_text="Enter a valid email address.")
    profile_image = forms.ImageField(required=False, help_text="Optional: Upload a profile image.")

    class Meta:
        model = CustomUser  # Use your custom user model
        fields = ["username", "email", "password1", "password2", "profile_image"]

    def save(self, commit=True):
        """
        Save the user instance with additional fields.
        """
        # Create a user instance without immediately saving to the database
        user = super().save(commit=False)

        # Set additional fields manually
        user.email = self.cleaned_data['email']
        image = self.cleaned_data.get('profile_image')

        # If a profile image was uploaded, assign it to the user
        if image:
            user.profile_image = image

        # Save the user object if commit=True
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

    username = forms.EmailField(label="Email", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
