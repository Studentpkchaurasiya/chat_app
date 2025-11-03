from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Message, Contact
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib import messages

def home(request):
    return render(request, "home.html")


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
            return redirect("personal_contact")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def personal_contact(request):
    if request.method == "POST":
        username = request.POST.get("username")
        if username:
            try:
                contact_user = User.objects.get(username=username)
                if contact_user == request.user:
                    messages.error(request, "You cannot add yourself.")
                else:
                    Contact.objects.get_or_create(user=request.user, contact_user=contact_user)
                    messages.success(request, f"{username} added successfully.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        return redirect("personal_contact")

    contacts = Contact.objects.filter(user=request.user).select_related("contact_user")

    return render(request, "personal_contact.html", {"contacts": contacts})
        

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

