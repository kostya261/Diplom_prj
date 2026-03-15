from django.contrib.auth.decorators import login_required
from inventory.models import Tool, ToolCategory, ToolManufacturer, StorageLocation, ToolIssue
from django.shortcuts import render, redirect, get_object_or_404
from core.utils import render_to_pdf
from users.models import User


# ========== КАТЕГОРИИ ==========
@login_required
def category_list(request):
    categories = ToolCategory.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})


@login_required
def category_form(request, category_id=None):
    """Создание или редактирование категории инструмента"""
    if category_id:
        category = get_object_or_404(ToolCategory, id=category_id)
        title = f"Редактирование: {category.name}"
    else:
        category = None
        title = "Добавление категории"

    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent_category')
        is_active = request.POST.get('is_active') == 'on'

        if category:
            category.name = name
            category.parent_category_id = parent_id if parent_id else None
            category.is_active = is_active
            category.save()
        else:
            category = ToolCategory.objects.create(
                name=name,
                parent_category_id=parent_id if parent_id else None,
                is_active=is_active
            )

        return redirect('category_list')

    # Для GET запроса — показать форму
    categories = ToolCategory.objects.all()
    return render(request, 'inventory/category_form.html', {
        'category': category,
        'categories': categories,
        'title': title,
        'action_url': request.path
    })


# ========== ПРОИЗВОДИТЕЛИ ==========
@login_required
def manufacturer_list(request):
    manufacturers = ToolManufacturer.objects.all()
    return render(request, 'inventory/manufacturer_list.html', {'manufacturers': manufacturers})


@login_required
def manufacturer_form(request, manufacturer_id=None):
    if manufacturer_id:
        manufacturer = get_object_or_404(ToolManufacturer, id=manufacturer_id)
        title = f"Редактирование: {manufacturer.name}"
    else:
        manufacturer = None
        title = "Добавление производителя"

    if request.method == 'POST':
        name = request.POST.get('name')
        country = request.POST.get('country', '')
        website = request.POST.get('website', '')
        is_active = request.POST.get('is_active') == 'on'

        if manufacturer:
            manufacturer.name = name
            manufacturer.country = country
            manufacturer.website = website
            manufacturer.is_active = is_active
            manufacturer.save()
        else:
            manufacturer = ToolManufacturer.objects.create(
                name=name,
                country=country,
                website=website,
                is_active=is_active
            )
        return redirect('manufacturer_list')

    return render(request, 'inventory/manufacturer_form.html', {
        'manufacturer': manufacturer,
        'title': title,
        'action_url': request.path
    })


# ========== МЕСТА ХРАНЕНИЯ ==========
@login_required
def location_list(request):
    locations = StorageLocation.objects.all()
    return render(request, 'inventory/location_list.html', {'locations': locations})


@login_required
def location_form(request, location_id=None):
    if location_id:
        location = get_object_or_404(StorageLocation, id=location_id)
        title = f"Редактирование: {location.name}"
    else:
        location = None
        title = "Добавление места хранения"

    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code', '')
        location_type = request.POST.get('location_type', 'warehouse')
        parent_id = request.POST.get('parent_location')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'

        if location:
            location.name = name
            location.code = code
            location.location_type = location_type
            location.parent_location_id = parent_id if parent_id else None
            location.description = description
            location.is_active = is_active
            location.save()
        else:
            location = StorageLocation.objects.create(
                name=name,
                code=code,
                location_type=location_type,
                parent_location_id=parent_id if parent_id else None,
                description=description,
                is_active=is_active
            )
        return redirect('location_list')

    locations = StorageLocation.objects.all()
    return render(request, 'inventory/location_form.html', {
        'location': location,
        'locations': locations,
        'title': title,
        'action_url': request.path
    })


@login_required
def tool_list(request):
    tools = Tool.objects.all().select_related('category', 'manufacturer', 'location')
    return render(request, 'inventory/tool_list.html', {'tools': tools})


@login_required
def tool_form(request, tool_id=None):
    """Создание или редактирование инструмента"""
    categories = ToolCategory.objects.filter(is_active=True)
    manufacturers = ToolManufacturer.objects.filter(is_active=True)
    locations = StorageLocation.objects.filter(is_active=True)

    if tool_id:
        tool = get_object_or_404(Tool, id=tool_id)
        title = f"Редактирование: {tool.name}"
    else:
        tool = None
        title = "Добавление инструмента"

    if request.method == 'POST':
        data = request.POST
        files = request.FILES

        if tool:
            # Обновление существующего
            tool.name = data.get('name')
            tool.inventory_number = data.get('inventory_number')
            tool.serial_number = data.get('serial_number', '')
            tool.model = data.get('model', '')
            tool.status = data.get('status', 'available')
            tool.condition = data.get('condition', '')

            year = data.get('year_of_manufacture')
            if year:
                tool.year_of_manufacture = int(year)

            purchase_date = data.get('purchase_date')
            if purchase_date:
                tool.purchase_date = purchase_date

            purchase_cost = data.get('purchase_cost')
            if purchase_cost:
                tool.purchase_cost = purchase_cost

            # Связи
            category_id = data.get('category')
            if category_id:
                tool.category_id = category_id

            manufacturer_id = data.get('manufacturer')
            if manufacturer_id:
                tool.manufacturer_id = manufacturer_id

            location_id = data.get('location')
            if location_id:
                tool.location_id = location_id

            # Фото
            if 'photo' in files:
                tool.photo = files['photo']

            tool.save()

        else:
            # Создание нового
            tool = Tool(
                name=data.get('name'),
                inventory_number=data.get('inventory_number'),
                serial_number=data.get('serial_number', ''),
                model=data.get('model', ''),
                status=data.get('status', 'available'),
                condition=data.get('condition', '')
            )

            if data.get('year_of_manufacture'):
                tool.year_of_manufacture = int(data.get('year_of_manufacture'))

            if data.get('purchase_date'):
                tool.purchase_date = data.get('purchase_date')

            if data.get('purchase_cost'):
                tool.purchase_cost = data.get('purchase_cost')

            # Связи
            category_id = data.get('category')
            if category_id:
                tool.category_id = category_id

            manufacturer_id = data.get('manufacturer')
            if manufacturer_id:
                tool.manufacturer_id = manufacturer_id

            location_id = data.get('location')
            if location_id:
                tool.location_id = location_id

            # Фото
            if 'photo' in files:
                tool.photo = files['photo']

            tool.save()

        return redirect('tool_list')

    return render(request, 'inventory/tool_form.html', {
        'tool': tool,
        'categories': categories,
        'manufacturers': manufacturers,
        'locations': locations,
        'title': title,
        'action_url': request.path
    })


# ========== ВЫДАЧА ИНСТРУМЕНТА ==========
@login_required
def issue_list(request):
    issues = ToolIssue.objects.all().select_related('tool', 'issued_to', 'issued_by', 'returned_to')
    return render(request, 'inventory/issue_list.html', {'issues': issues})


def issue_form(request, issue_id=None):
    tools = Tool.objects.filter(status='available')
    employees = User.objects.filter(is_active=True)

    if issue_id:
        issue = get_object_or_404(ToolIssue, id=issue_id)
        title = "Редактирование выдачи"
    else:
        issue = None
        title = "Выдача инструмента"

    if request.method == 'POST':
        tool_id = request.POST.get('tool')
        issued_to_id = request.POST.get('issued_to')
        expected_return = request.POST.get('expected_return_at')
        notes = request.POST.get('notes', '')

        if issue:
            issue.expected_return_at = expected_return if expected_return else None
            issue.notes = notes
            issue.save()
        else:
            issue = ToolIssue.objects.create(
                tool_id=tool_id,
                issued_to_id=issued_to_id,
                issued_by=request.user if request.user.is_authenticated else employees.first(),
                expected_return_at=expected_return if expected_return else None,
                notes=notes
            )
            # Обновляем статус инструмента
            tool = Tool.objects.get(id=tool_id)
            tool.status = 'in_use'
            tool.save()

        return redirect('issue_list')

    return render(request, 'inventory/issue_form.html', {
        'issue': issue,
        'tools': tools,
        'employees': employees,
        'title': title,
        'action_url': request.path
    })


@login_required
def return_tool(request, issue_id):
    issue = get_object_or_404(ToolIssue, id=issue_id)
    if request.method == 'POST':
        issue.return_tool(request.user, request.POST.get('notes', ''))
    return redirect('issue_list')


@login_required
def tool_report(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)
    return render_to_pdf(
        'inventory/tool_report.html',
        {'tool': tool},
        filename=f'tool_{tool_id}.pdf'
    )


@login_required
def issue_report(request, issue_id):
    issue = get_object_or_404(ToolIssue, id=issue_id)
    return render_to_pdf(
        'inventory/issue_report.html',
        {'issue': issue},
        filename=f'issue_{issue_id}.pdf'
    )


@login_required
def employee_tools(request):
    active_issues = ToolIssue.objects.filter(
        returned_at__isnull=True
    ).select_related('tool', 'issued_to', 'issued_by').order_by('issued_to__last_name')

    return render(request, 'inventory/employee_tools.html', {
        'active_issues': active_issues
    })
