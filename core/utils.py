import pdfkit
from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict={}, filename='document.pdf'):
    """
    Универсальная функция для генерации PDF.
    Использует путь к wkhtmltopdf из settings.WKHTMLTOPDF_PATH.
    """
    # Загружаем и рендерим шаблон
    template = get_template(template_src)
    html = template.render(context_dict)

    # Базовые опции для PDF
    options = {
        'encoding': 'UTF-8',
        'quiet': '',
        'page-size': 'A4',
        'margin-top': '15mm',
        'margin-right': '15mm',
        'margin-bottom': '15mm',
        'margin-left': '15mm',
    }

    # Настраиваем конфигурацию wkhtmltopdf
    config = None
    wkhtmltopdf_path = getattr(settings, 'WKHTMLTOPDF_PATH', 'wkhtmltopdf')

    # Если путь указан и отличается от значения по умолчанию
    if wkhtmltopdf_path and wkhtmltopdf_path != 'wkhtmltopdf':
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # Генерируем PDF
    try:
        pdf = pdfkit.from_string(html, False, options=options, configuration=config)

        # Возвращаем ответ
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response

    except OSError as e:
        # Если не удалось найти wkhtmltopdf
        return HttpResponse(
            f'Ошибка генерации PDF: {str(e)}. Проверьте настройки WKHTMLTOPDF_PATH.',
            status=500
        )
    except Exception as e:
        # Любая другая ошибка
        return HttpResponse(
            f'Неизвестная ошибка при генерации PDF: {str(e)}',
            status=500
        )
