from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('index')  # Перенаправление на главную страницу
        else:
            messages.error(request, 'Ошибка при регистрации. Пожалуйста, проверьте данные.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form}) 