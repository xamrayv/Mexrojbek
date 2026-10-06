from django.urls import path
from .views import (
    home_view,
    login_view,
    google_login_view,
    google_callback_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('auth/google-login/', google_login_view, name='google_login'),
    path('auth/google/callback/', google_callback_view, name='google_callback'),
]