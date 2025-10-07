from django.shortcuts import redirect, render

def home(request):
    if request.user.is_authenticated:
        return redirect('/admin/')
    return render(request, 'home.html')