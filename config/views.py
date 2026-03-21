from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages


def index(request):
    return render(request, 'index.html')


def employee_load_report(request):
    return render(request, 'reports/employee_load.html')


def important_tasks_report(request):
    return render(request, 'reports/important_tasks.html')


@login_required
def profile_view(request):
    return render(request, 'profile.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user

        # Обновляем основные поля
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.save()

        # Смена пароля
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if old_password and new_password1 and new_password2:
            if user.check_password(old_password):
                if new_password1 == new_password2:
                    user.set_password(new_password1)
                    user.save()
                    update_session_auth_hash(request, user)  # не разлогинивает после смены пароля
                    messages.success(request, 'Пароль успешно изменён')
                else:
                    messages.error(request, 'Новые пароли не совпадают')
            else:
                messages.error(request, 'Неверный старый пароль')

        return redirect('profile')

    return render(request, 'profile_edit.html')
