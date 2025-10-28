# apps.core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from django.core.mail import send_mail
import random
from django.conf import settings
from typing import cast


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


from django.contrib.auth import get_user_model
User = get_user_model()

# def login_view(request):
#     if request.method == 'POST':
#         form = UserLoginForm(request, data=request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')

#             user = authenticate(request, username=email, password=password)

#             if user is not None:
#                 # 🚫 Check if blocked
#                 if getattr(user, 'is_blocked', False):
#                     messages.error(request, "Your account has been blocked by the admin.")
#                     return redirect('login')

#                 login(request, user)
#                 messages.success(request, f"Welcome, {user.username}!")
#                 return redirect('dashboard')
#             else:
#                 messages.error(request, "Invalid email or password.")
#     else:
#         form = UserLoginForm()

#     return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect('home')

@login_required
def dashboard_view(request):
    return render(request, "accounts/dashboard.html")

# --------------------------------------------
# Admin Settings View
# --------------------------------------------
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

@login_required
def admin_settings_view(request):
    all_users = CustomUser.objects.exclude(id=request.user.id)
    user = request.user

    if request.method == "POST":
        # Profile updates
        if "first_name" in request.POST:
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.email = request.POST.get("email")

            # 📸 Profile Image Upload
            if "profile_image" in request.FILES:
                user.profile_image = request.FILES["profile_image"]

            # 🔑 Password Change
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if current_password or new_password or confirm_password:
                if not user.check_password(current_password):
                    messages.error(request, "❌ Current password is incorrect.")
                    return redirect("admin_settings")
                if new_password != confirm_password:
                    messages.error(request, "⚠️ New passwords do not match.")
                    return redirect("admin_settings")
                user.set_password(new_password)
                update_session_auth_hash(request, user)
                messages.success(request, "🔐 Password changed successfully!")

            user.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect("admin_settings")

        # 🔒 Block / Unblock users
        block_user_id = request.POST.get("block_user")
        if block_user_id:
            try:
                target_user = CustomUser.objects.get(id=block_user_id)
                action = request.POST.get("action")
                if action == "block":
                    target_user.is_blocked = True
                    target_user.save()
                    messages.success(request, f"{target_user.username} has been blocked.")
                elif action == "unblock":
                    target_user.is_blocked = False
                    target_user.save()
                    messages.success(request, f"{target_user.username} has been unblocked.")
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")

        # 👁️ Private/Public account toggle
        if "privateAccount" in request.POST:
            user.is_private = True
        else:
            user.is_private = False
        user.save()

        messages.success(request, "Settings updated successfully!")
        return redirect("admin_settings")

    return render(request, "accounts/admin_settings.html", {"all_users": all_users})


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    all_users = CustomUser.objects.exclude(id=request.user.id)

    # 👑 Superuser can view everyone (including private)
    if request.user.is_superuser:
        context = {"profile_user": profile_user, "all_users": all_users}
        return render(request, "accounts/profile.html", context)

    # 🚫 Restrict private profiles for non-superusers
    if profile_user.is_private and request.user != profile_user:
        messages.warning(request, "🚫 This account is private.")
        return redirect("dashboard")

    # 👩‍💼 Staff logic: can view staff + active normal users
    if request.user.is_staff:
        if not (
            profile_user.is_staff
            or (profile_user.is_active and not profile_user.is_superuser and not profile_user.is_blocked)
            or request.user == profile_user
        ):
            messages.warning(request, "🚫 Staff can only view staff or active user profiles.")
            return redirect("dashboard")

    # 👤 Normal user logic: can view only active, normal users (non-staff, non-superuser)
    elif not request.user.is_staff and not request.user.is_superuser:
        if not (
            profile_user.is_active
            and not profile_user.is_superuser
            and not profile_user.is_staff
            and not profile_user.is_blocked
        ) and request.user != profile_user:
            messages.warning(request, "🚫 You can only view other active user profiles.")
            return redirect("dashboard")

    context = {"profile_user": profile_user, "all_users": all_users}
    return render(request, "accounts/profile.html", context)


def generate_otp():
    return str(random.randint(100000, 999999))

# --------------------------------------------
# Login View (with 2FA)
# --------------------------------------------
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=email, password=password)

            if user is not None:
                user = cast(CustomUser, user)

                if user.is_blocked:
                    messages.error(request, "🚫 Your account has been blocked by the admin.")
                    return redirect('login')

                # ✅ If user has 2FA enabled
                if getattr(user, "two_factor_enabled", False):
                    otp = generate_otp()
                    user.otp_code = otp
                    user.save()

                    send_mail(
                        subject="Your ShopEase Login OTP",
                        message=f"Your OTP is: {otp}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )

                    print(f"[DEBUG] OTP for {user.email}: {otp}")
                    request.session['pending_2fa_user'] = user.id  # type: ignore
                    return redirect('verify_otp')

                # ✅ Normal login
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('dashboard')

            else:
                messages.error(request, "❌ Invalid email or password.")
                return render(request, "accounts/login.html", {"form": form})

        else:
            messages.error(request, "⚠️ Please correct the errors below.")
            return render(request, "accounts/login.html", {"form": form})

    # ✅ Handle GET requests (when user opens the page)
    else:
        form = UserLoginForm()
        return render(request, "accounts/login.html", {"form": form})
# --------------------------------------------
# Verify OTP View
# --------------------------------------------
from django.contrib.auth import get_backends


def verify_otp_view(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_id = request.session.get('pending_2fa_user')

        if not user_id:
            messages.error(request, "Session expired. Please log in again.")
            return redirect('login')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')

        if user.otp_code == otp:
            # ✅ Clear OTP and session
            user.otp_code = None
            user.save()
            del request.session['pending_2fa_user']

            # ✅ Attach backend explicitly before login
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}" # type: ignore

            # ✅ Log the user in
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'accounts/verify_otp.html')

from django.contrib.auth import get_user_model
User = get_user_model()



def update_privacy_security(request):
    if request.method == 'POST':
        user: CustomUser = request.user  # 👈 helps Pylance know it's your model
        action = request.POST.get('action')

        if action == 'enable_2fa':
            user.two_factor_enabled = True
        elif action == 'disable_2fa':
            user.two_factor_enabled = False

        user.is_private = 'privateAccount' in request.POST

        target_user_id = request.POST.get('block_user')
        if target_user_id:
            try:
                target_user: CustomUser = User.objects.get(id=target_user_id)  # type: ignore
                if action == 'block':
                    target_user.is_blocked = True
                elif action == 'unblock':
                    target_user.is_blocked = False
                target_user.save()
            except User.DoesNotExist:
                pass

        user.save()
        return redirect('admin_settings')
    
    
# reset password ?

from datetime import datetime, timedelta

RESET_OTP_STORAGE = {}  # { email: {"otp": "123456", "expires": datetime }}

def forgot_password_view(request):
    """Step 1: Ask user email and send OTP"""
    if request.method == "POST":
        email = request.POST.get("email")
        user = CustomUser.objects.filter(email=email).first()

        if not user:
            messages.error(request, "❌ This email is not registered.")
            return redirect("forgot_password")

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        RESET_OTP_STORAGE[email] = {
            "otp": otp,
            "expires": datetime.now() + timedelta(minutes=5)
        }

        # Send OTP via email
        send_mail(
            subject="ShopEase Password Reset OTP",
            message=f"Your OTP for password reset is: {otp}. It will expire in 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

        print(f"[DEBUG] Reset OTP for {email}: {otp}")  # Debug only

        request.session["reset_email"] = email
        messages.info(request, "📧 OTP has been sent to your email.")
        return redirect("verify_reset_otp")

    return render(request, "accounts/forgot_password.html")


def verify_reset_otp_view(request):
    """Step 2: Verify OTP"""
    email = request.session.get("reset_email")

    if not email:
        messages.error(request, "Session expired. Please try again.")
        return redirect("forgot_password")

    if request.method == "POST":
        otp = request.POST.get("otp")
        record = RESET_OTP_STORAGE.get(email)

        if record and record["otp"] == otp and datetime.now() < record["expires"]:
            # OTP verified
            request.session["otp_verified"] = True
            messages.success(request, "✅ OTP verified successfully.")
            return redirect("reset_password")
        else:
            messages.error(request, "⚠️ Invalid or expired OTP.")
            return redirect("verify_reset_otp")

    return render(request, "accounts/verify_reset_otp.html")


def reset_password_view(request):
    """Step 3: Allow user to reset password"""
    email = request.session.get("reset_email")
    otp_verified = request.session.get("otp_verified", False)

    if not email or not otp_verified:
        messages.error(request, "Unauthorized access.")
        return redirect("forgot_password")

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        user = CustomUser.objects.filter(email=email).first()
        if user:
            user.set_password(password1)
            user.save()

            # Cleanup session + OTP
            RESET_OTP_STORAGE.pop(email, None)
            request.session.pop("reset_email", None)
            request.session.pop("otp_verified", None)

            messages.success(request, "🎉 Password reset successful! Please login.")
            return redirect("login")

    return render(request, "accounts/reset_password.html")