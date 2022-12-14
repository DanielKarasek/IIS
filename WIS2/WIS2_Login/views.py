from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


# Create your views here.
def register(response):
    if response.method == 'POST':
        form = UserCreationForm(response.POST)
        if form.is_valid():
            # create new user
            form.save()
            return redirect('/login/')
    else:
        form = UserCreationForm()
    return render(response, 'register.html', {'form': form})
