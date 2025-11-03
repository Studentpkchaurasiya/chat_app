from django.urls import path
from . import views

urlpatterns=[
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("chat/", views.personal_contact, name="personal_contact"),
    path("chat/<str:username>/", views.chat_view, name="chat"),
]