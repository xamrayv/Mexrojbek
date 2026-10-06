from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import User
import requests
from urllib.parse import urlencode
from django.conf import settings
import secrets

# Create your views here.

@login_required(login_url='login')
def home_view(request):
    return render(
        request,
        'home.html'
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect(
            'home'
        )

    return render(
        request,
        'login.html'
    )

"""
    google_login_view,
    google_callback_view
"""

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def google_login_view(request):
    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.LOGIN_REDIRECT_URL,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": state,  # <-- shu yerga qo'shildi
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return redirect(url)


def google_callback_view(request):
    code = request.GET.get("code")
    returned_state = request.GET.get("state")
    saved_state = request.session.pop("google_oauth_state", None)

    # state tekshiruvi
    if not returned_state or returned_state != saved_state:
        return redirect("login")  # yoki 403 xato qaytarish mumkin
    if not code:
        return redirect("login")

    # 1) code -> access_token almashtirish
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.LOGIN_REDIRECT_URL,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data).json()
    access_token = token_response.get("access_token")

    if not access_token:
        return redirect("login")

    # 2) access_token bilan user ma'lumotini olish
    user_info = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    email = user_info.get("email")
    first_name = user_info.get("given_name", "")
    picture = user_info.get("picture", "")

    if not email:
        return redirect("login")

    # 3) User yaratish yoki topish
    user, created = User.objects.get_or_create(
        username=email,
        defaults={
            "email": email, "first_name": first_name, 'profile': picture
        },
    )


    login(request, user)
    return redirect("home")