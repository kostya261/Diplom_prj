from weasyprint import HTML
from django.template.loader import get_template
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict={}, filename='document.pdf'):
    """
    Генерирует PDF из HTML-шаблона с помощью WeasyPrint.
    """
    template = get_template(template_src)
    html_string = template.render(context_dict)

    # Генерируем PDF
    html = HTML(string=html_string, encoding='utf-8')
    pdf = html.write_pdf()

    # Возвращаем ответ
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
