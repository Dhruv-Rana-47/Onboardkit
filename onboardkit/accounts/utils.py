# accounts/utils.py

from django.core.exceptions import PermissionDenied

def authority_required(code):
    """
    Decorator to check if the logged-in user has a specific authority code.
    If the user is not authenticated or lacks the required authority, a PermissionDenied is raised.
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                raise PermissionDenied("Login required.")
            if not user.role or not user.role.has_authority(code):
                raise PermissionDenied("You don't have the required authority.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
