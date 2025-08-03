def user_authorities(request):
    if request.path.startswith("/admin/") or not request.user.is_authenticated:
        return {}
    
    if request.user.is_authenticated:
        # Fetch authorities based on your permission system
        authorities = set(
            request.user.role.authorities.values_list('code', flat=True)
        ) if hasattr(request.user, 'role') else set()
        
        return {
            'authorities': authorities
        }
    return {}


# >>>later implement this change below with upper code ,to not get erro when run first time
