from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    """
    A custom authentication backend. Allows users to log in using their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        
        # --- LOUD DEBUGGING ---
        # This will print to your terminal every time a login attempt is made.
        print("--- AUTHENTICATING VIA CUSTOM EMAIL BACKEND ---")
        # --- END DEBUGGING ---

        UserModel = get_user_model()
        try:
            # Try to fetch the user by looking up the email field.
            # 'iexact' makes the lookup case-insensitive.
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            # If no user is found with that email, authentication fails.
            print(f"Login failed: No user found with email '{username}'")
            return None
        
        # Check if the password is correct for the user we found.
        if user.check_password(password):
            print(f"Login successful for user: {user.email}")
            return user # Return the user object if authentication is successful
        else:
            print(f"Login failed: Incorrect password for user '{username}'")
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None