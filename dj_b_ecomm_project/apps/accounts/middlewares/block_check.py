# middlewares/block_check.py
from django.shortcuts import redirect
from django.contrib import messages

class BlockCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_blocked:
            from django.contrib.auth import logout
            logout(request)
            messages.error(request, "Your account is blocked by admin.")
            return redirect("login")
        return self.get_response(request)
