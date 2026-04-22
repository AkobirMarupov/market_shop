from rest_framework_simplejwt.authentication import JWTAuthentication

def get_user_from_request(request):
    auth = JWTAuthentication()
    
    user_auth_tuple = auth.authenticate(request)
    
    if user_auth_tuple is None:
        return None
        
    user, token = user_auth_tuple
    
    user_id = user.id
    role = getattr(user, 'role', None)
    
    return {
        "user": user, 
        "user_id": user_id, 
        "role": role
    }