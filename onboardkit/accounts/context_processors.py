def user_authorities(request):
    if request.user.is_authenticated:
        # Fetch authorities based on your permission system
        authorities = set(
            request.user.role.authorities.values_list('code', flat=True)
        ) if hasattr(request.user, 'role') else set()
        
        return {
            'authorities': authorities
        }
    return {}