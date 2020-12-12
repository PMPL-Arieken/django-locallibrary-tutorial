from django.contrib.auth.models import User
from django.contrib.auth import login
from register.forms import RegisterForm
from django.shortcuts import redirect, render

# Create your views here.


def index(request):
    if request.method == 'GET':
        register_form = RegisterForm()
    else:
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user = User.objects.create_user(
                username=register_form.data.get('email'),
                email=register_form.data.get('email'),
                password=register_form.data.get('password'))
            user.save()
            login(request, user)
            return redirect("/")

    return render(request, 'register.html', {'form': register_form})
