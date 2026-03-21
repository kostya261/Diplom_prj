from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from inventory.models import StorageLocation
from users.models import User
from tasks.models import Task
from warehouse.models import Product, ProductCategory, ProductManufacturer
from warehouse.models import StockMovement
from django.db import transaction
from decimal import Decimal
from core.utils import render_to_pdf


# ========== КАТЕГОРИИ ТОВАРОВ ==========
@login_required
def category_list(request):
    categories = ProductCategory.objects.all()
    return render(request, 'warehouse/category_list.html', {'categories': categories})


@login_required
def category_form(request, category_id=None):
    if category_id:
        category = get_object_or_404(ProductCategory, id=category_id)
        title = f"Редактирование: {category.name}"
    else:
        category = None
        title = "Добавление категории товаров"

    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent_category')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'

        if category:
            category.name = name
            category.parent_category_id = parent_id if parent_id else None
            category.description = description
            category.is_active = is_active
            category.save()
        else:
            category = ProductCategory.objects.create(
                name=name,
                parent_category_id=parent_id if parent_id else None,
                description=description,
                is_active=is_active
            )
        return redirect('warehouse_category_list')

    categories = ProductCategory.objects.all()
    return render(request, 'warehouse/category_form.html', {
        'category': category,
        'categories': categories,
        'title': title,
        'action_url': request.path
    })


# ========== ПРОИЗВОДИТЕЛИ ТОВАРОВ ==========
@login_required
def manufacturer_list(request):
    manufacturers = ProductManufacturer.objects.all()
    return render(request, 'warehouse/manufacturer_list.html', {'manufacturers': manufacturers})


@login_required
def manufacturer_form(request, manufacturer_id=None):
    if manufacturer_id:
        manufacturer = get_object_or_404(ProductManufacturer, id=manufacturer_id)
        title = f"Редактирование: {manufacturer.name}"
    else:
        manufacturer = None
        title = "Добавление производителя товаров"

    if request.method == 'POST':
        name = request.POST.get('name')
        country = request.POST.get('country', '')
        website = request.POST.get('website', '')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'

        if manufacturer:
            manufacturer.name = name
            manufacturer.country = country
            manufacturer.website = website
            manufacturer.description = description
            manufacturer.is_active = is_active
            manufacturer.save()
        else:
            manufacturer = ProductManufacturer.objects.create(
                name=name,
                country=country,
                website=website,
                description=description,
                is_active=is_active
            )
        return redirect('warehouse_manufacturer_list')

    return render(request, 'warehouse/manufacturer_form.html', {
        'manufacturer': manufacturer,
        'title': title,
        'action_url': request.path
    })


@login_required
def product_list(request):
    products = Product.objects.all().select_related('category', 'manufacturer')
    return render(request, 'warehouse/product_list.html', {'products': products})


@login_required
def product_form(request, product_id=None):
    """Создание или редактирование товара"""
    categories = ProductCategory.objects.filter(is_active=True)
    manufacturers = ProductManufacturer.objects.filter(is_active=True)
    locations = StorageLocation.objects.filter(is_active=True)

    if product_id:
        product = get_object_or_404(Product, id=product_id)
        title = f"Редактирование: {product.name}"
    else:
        product = None
        title = "Добавление товара"

    if request.method == 'POST':
        data = request.POST
        files = request.FILES

        if product:
            # Обновление существующего
            product.article = data.get('article')
            product.name = data.get('name')
            product.description = data.get('description', '')
            product.unit = data.get('unit', 'шт')
            location_id = data.get('location')
            product.location_id = location_id if location_id else None
            product.barcode = data.get('barcode', '')
            product.is_active = data.get('is_active') == 'on'

            # Количество
            if not product.pk:
                quantity = data.get('quantity')
                if quantity:
                    product.quantity = quantity

            min_qty = data.get('min_quantity')
            if min_qty:
                product.min_quantity = min_qty

            max_qty = data.get('max_quantity')
            if max_qty:
                product.max_quantity = max_qty

            purchase_price = data.get('purchase_price')
            if purchase_price:
                product.purchase_price = purchase_price

            selling_price = data.get('selling_price')
            if selling_price:
                product.selling_price = selling_price

            # Связи
            category_id = data.get('category')
            if category_id:
                product.category_id = category_id
            else:
                product.category = None

            manufacturer_id = data.get('manufacturer')
            if manufacturer_id:
                product.manufacturer_id = manufacturer_id
            else:
                product.manufacturer = None

            # Фото
            if 'photo' in files:
                product.photo = files['photo']

            product.save()

        else:
            # Создание нового
            product = Product(
                article=data.get('article'),
                name=data.get('name'),
                description=data.get('description', ''),
                unit=data.get('unit', 'шт'),

                barcode=data.get('barcode', ''),
                is_active=data.get('is_active') == 'on'

            )
            location_id = data.get('location')
            if location_id:
                product.location_id = location_id

            # Количество
            quantity = data.get('quantity')
            if quantity:
                product.quantity = quantity

            min_qty = data.get('min_quantity')
            if min_qty:
                product.min_quantity = min_qty

            max_qty = data.get('max_quantity')
            if max_qty:
                product.max_quantity = max_qty

            purchase_price = data.get('purchase_price')
            if purchase_price:
                product.purchase_price = purchase_price

            selling_price = data.get('selling_price')
            if selling_price:
                product.selling_price = selling_price

            # Связи
            category_id = data.get('category')
            if category_id:
                product.category_id = category_id

            manufacturer_id = data.get('manufacturer')
            if manufacturer_id:
                product.manufacturer_id = manufacturer_id

            # Фото
            if 'photo' in files:
                product.photo = files['photo']

            product.save()

        return redirect('product_list')

    return render(request, 'warehouse/product_form.html', {
        'product': product,
        'categories': categories,
        'manufacturers': manufacturers,
        'locations': locations,
        'title': title,
        'action_url': request.path
    })


@login_required
def movement_form(request):
    """Создание движения (приход/расход)"""
    products = Product.objects.filter(is_active=True)
    tasks = Task.objects.all()

    selected_product = request.GET.get('product')
    movement_type = request.GET.get('type', 'incoming')

    if request.method == 'POST':
        data = request.POST

        from decimal import Decimal
        quantity = Decimal(data.get('quantity'))

        movement = StockMovement(
            product_id=data.get('product'),
            movement_type=data.get('movement_type'),
            quantity=quantity,
            document_number=data.get('document_number', ''),
            comment=data.get('comment', '')
        )

        task_id = data.get('task')
        if task_id:
            movement.task_id = task_id

        # created_by нужно будет брать из текущего пользователя
        # пока ставим админа или первого попавшегося
        movement.created_by = User.objects.filter(role='admin').first()

        movement.save()

        return redirect('product_list')

    return render(request, 'warehouse/movement_form.html', {
        'products': products,
        'tasks': tasks,
        'selected_product': int(selected_product) if selected_product else None,
        'movement_type': movement_type,
        'title': 'Добавление движения',
        'action_url': '/warehouse/movements/add/'
    })


@login_required
def movement_list(request):
    movements = StockMovement.objects.all().select_related('product', 'task', 'created_by').order_by('-created_at')
    return render(request, 'warehouse/movement_list.html', {'movements': movements})


# ========== ОТЧЁТЫ ==========


@login_required
def report_stock_balance(request):
    categories = ProductCategory.objects.prefetch_related('products').all()
    return render_to_pdf(
        'warehouse/reports/stock_balance.html',
        {'categories': categories},
        filename='ostatki_sklada.pdf'
    )


@login_required
def report_inventory(request):
    # Если это просто заход на страницу без параметров — показываем выбор
    if not request.GET.get('location'):
        locations = StorageLocation.objects.filter(is_active=True)
        return render(request, 'warehouse/inventory_select.html', {'locations': locations})

    # Если параметр есть — генерируем PDF
    products = Product.objects.all().select_related('category')
    products = products.filter(location_id=request.GET['location'])

    return render_to_pdf(
        'warehouse/reports/inventory.html',
        {'products': products},
        filename='inventarizaciya.pdf'
    )


@login_required
def report_incoming(request, movement_id):
    movement = get_object_or_404(StockMovement, id=movement_id)
    return render_to_pdf(
        'warehouse/reports/incoming.html',
        {'movement': movement},
        filename=f'prihod_{movement_id}.pdf'
    )


@login_required
def report_outgoing(request, movement_id):
    movement = get_object_or_404(StockMovement, id=movement_id)
    return render_to_pdf(
        'warehouse/reports/outgoing.html',
        {'movement': movement},
        filename=f'rasxod_{movement_id}.pdf'
    )


@login_required
def transfer_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        from_location_id = request.POST.get('from_location')
        to_location_id = request.POST.get('to_location')
        quantity = Decimal(request.POST.get('quantity'))
        comment = request.POST.get('comment', '')

        with transaction.atomic():
            # 1. Расход с исходного склада
            StockMovement.objects.create(
                product_id=product_id,
                movement_type='outgoing',
                quantity=quantity,
                from_location_id=from_location_id,
                to_location_id=to_location_id,
                comment=f"Перемещение: {comment}",
                created_by=request.user
            )

            # 2. Приход на целевой склад
            StockMovement.objects.create(
                product_id=product_id,
                movement_type='incoming',
                quantity=quantity,
                from_location_id=from_location_id,
                to_location_id=to_location_id,
                comment=f"Перемещение: {comment}",
                created_by=request.user
            )

        return redirect('movement_list')

    # GET — показать форму
    products = Product.objects.filter(is_active=True)
    locations = StorageLocation.objects.filter(is_active=True)
    return render(request, 'warehouse/transfer_form.html', {
        'products': products,
        'locations': locations
    })
