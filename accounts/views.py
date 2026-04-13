## serving the view to the user

from django.shortcuts import render, redirect # for renserinfg and redirectingt he pages
from django.contrib.auth import login, authenticate, logout # for authentication
from django.contrib.auth.decorators import login_required # validation 
from django.contrib import messages # for sedingthe messages
from django.contrib.auth.forms import UserCreationForm # can i chagne or add any filed to the usercreation form ?


def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # can i cange the size of the form 
            username = form.cleaned_data.get("username") 
            messages.success(request, f"Account created for {username}!")
            login(request, user) # so they don't have to relogin again 
            return redirect("core:home")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request): 
    if request.user.is_authenticated: 
        return redirect("core:home") 
    
    if request.method == "POST": 
        username = request.POST.get("username") 
        password = request.POST.get("password") 
        user = authenticate(request, username=username, password=password) 
        if user is not None: 
            login(request, user) 
            messages.success(request, f"Welcome back, {username}!")
            return redirect("core:home")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("core:home")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")
