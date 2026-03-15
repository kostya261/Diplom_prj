from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from tasks.models import Task
from users.models import User
from django.http import HttpResponse
from warehouse.views_web import render_to_pdf


@login_required
def task_list(request):
    tasks = Task.objects.all().select_related('responsible').prefetch_related('co_executors')
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_form(request, task_id=None):
    """Создание или редактирование задачи"""
    employees = User.objects.filter(is_active=True)
    tasks = Task.objects.all()

    if task_id:
        task = get_object_or_404(Task, id=task_id)
        title = f"Редактирование: {task.title}"
    else:
        task = None
        title = "Создание задачи"

    if request.method == 'POST':
        data = request.POST

        if task:
            # Обновление существующей
            task.title = data.get('title')
            task.description = data.get('description', '')
            task.priority = data.get('priority', 'medium')
            task.deadline = data.get('deadline')
            task.status = data.get('status', 'new')

            responsible_id = data.get('responsible')
            if responsible_id:
                task.responsible_id = responsible_id

            parent_id = data.get('parent_task')
            if parent_id:
                task.parent_task_id = parent_id
            else:
                task.parent_task = None

            task.save()

            # Обновляем соисполнителей
            co_executors_ids = data.getlist('co_executors')
            task.co_executors.set(co_executors_ids)

        else:
            # Создание новой
            task = Task.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                priority=data.get('priority', 'medium'),
                deadline=data.get('deadline'),
                status=data.get('status', 'new'),
                responsible_id=data.get('responsible'),
                created_by=request.user
            )

            parent_id = data.get('parent_task')
            if parent_id:
                task.parent_task_id = parent_id
                task.save()

            # Добавляем соисполнителей
            co_executors_ids = data.getlist('co_executors')
            if co_executors_ids:
                task.co_executors.set(co_executors_ids)

        return redirect('task_list')

    return render(request, 'tasks/task_form.html', {
        'task': task,
        'employees': employees,
        'tasks': tasks,
        'title': title,
        'action_url': request.path
    })


@login_required
def report_task_order(request, task_id):
    task = get_object_or_404(Task.objects.prefetch_related('stock_movements__product'), id=task_id)
    pdf = render_to_pdf('tasks/reports/task_order.html', {'task': task})
    if pdf:
        return pdf
    return HttpResponse('Ошибка генерации PDF', status=500)


@login_required
def task_order(request, task_id):
    task = get_object_or_404(Task.objects.prefetch_related(
        'stock_movements__product',
        'tool_issues__tool'
    ), id=task_id)
    return render_to_pdf(
        'tasks/task_order.html',
        {'task': task},
        filename=f'task_order_{task_id}.pdf'
    )


@login_required
def change_task_status(request, task_id, new_status):
    task = get_object_or_404(Task, id=task_id)

    # Проверяем права
    if (request.user.role == 'employee' and task.responsible != request.user
            and request.user not in task.co_executors.all()):
        messages.error(request, 'Вы можете менять статус только своих задач')
        return redirect('task_list')

    # Комментарий можно передавать через GET-параметр
    comment = request.GET.get('comment', '')

    if task.change_status(new_status, request.user, comment):
        messages.success(request, f'Статус задачи изменён на {task.get_status_display()}')
    else:
        messages.error(request, 'Не удалось изменить статус')

    return redirect('task_list')
