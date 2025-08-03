from django.shortcuts import redirect, render
from django.contrib.auth import logout

class CheckCompanyActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'company') and not request.user.company.is_active:
                logout(request)
                return render(request, 'auth/company_suspended.html')  # 👈 Renders suspended page
        return self.get_response(request)


# accounts/middleware.py

from django.shortcuts import redirect
from django.contrib.auth import logout

class CheckCompanyActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if hasattr(user, 'company') and user.company and not user.company.is_active:
                logout(request)
                return redirect(request, 'auth/company_suspended.html')  # or render a suspended page
        return self.get_response(request)
