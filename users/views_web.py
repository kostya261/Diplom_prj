from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from departments.models import Department

from users.models import User


def employee_list(request):
    employees = User.objects.all()
    return render(request, 'users/employee_list.html', {'employees': employees})


def employee_form(request, employee_id=None):
    """Создание или редактирование сотрудника"""
    departments = Department.objects.filter(is_active=True)

    if employee_id:
        # Редактирование
        employee = get_object_or_404(User, id=employee_id)
        title = f"Редактирование: {employee.get_full_name() or employee.username}"
    else:
        # Создание
        employee = None
        title = "Добавление сотрудника"

    if request.method == 'POST':
        data = request.POST.copy()

        if employee:
            # Обновление существующего
            for field in ['username', 'email', 'first_name', 'last_name', 'phone',
                          'position', 'role', 'passport_series', 'passport_number',
                          'passport_issued_by', 'passport_code', 'registration_address',
                          'residential_address', 'notes']:
                setattr(employee, field, data.get(field, ''))

            # Отдел
            dept_id = data.get('department')
            if dept_id:
                employee.department_id = dept_id
            else:
                employee.department = None

            # Дата выдачи паспорта
            passport_date = data.get('passport_issued_date')
            if passport_date:
                employee.passport_issued_date = passport_date
            else:
                employee.passport_issued_date = None

            employee.save()

        else:
            # Создание нового
            employee = User.objects.create(
                username=data.get('username'),
                email=data.get('email'),
                password=make_password(data.get('password')),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone=data.get('phone', ''),
                position=data.get('position', ''),
                role=data.get('role', 'employee'),
                passport_series=data.get('passport_series', ''),
                passport_number=data.get('passport_number', ''),
                passport_issued_by=data.get('passport_issued_by', ''),
                passport_code=data.get('passport_code', ''),
                registration_address=data.get('registration_address', ''),
                residential_address=data.get('residential_address', ''),
                notes=data.get('notes', '')
            )

            # Отдел
            dept_id = data.get('department')
            if dept_id:
                employee.department_id = dept_id
                employee.save()

            # Дата выдачи паспорта
            passport_date = data.get('passport_issued_date')
            if passport_date:
                employee.passport_issued_date = passport_date
                employee.save()

        return redirect('employee_list')

    return render(request, 'users/employee_form.html', {
        'employee': employee,
        'departments': departments,
        'title': title,
        'action_url': request.path
    })


@login_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(User, id=employee_id)
    return render(request, 'users/employee_detail.html', {'employee': employee})
