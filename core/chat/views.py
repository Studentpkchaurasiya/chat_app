from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Message
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]

        if password != confirm:
            return render(request, "register.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already taken"})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect("login")

    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("chat")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")




@login_required
def chat_view(request, username):
    recipient = get_object_or_404(User, username=username)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=recipient) |
        Q(sender=recipient, receiver=request.user)
    ).order_by("timestamp")

    return render(request, "chat.html", {
        "messages": messages,
        "recipient": recipient
    })

