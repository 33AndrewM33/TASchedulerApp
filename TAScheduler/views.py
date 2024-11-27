from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('/home/')
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/home/')  # Redirect to a placeholder after successful login
        else:
            error = "Invalid username or password"
    return render(request, "login.html", {"error": error})

def custom_logout(request):
    logout(request)
    return redirect('/')
