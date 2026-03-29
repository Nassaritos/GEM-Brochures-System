from io import BytesIO
from django.http import HttpResponse
from openpyxl import Workbook
from xhtml2pdf import pisa
from django.template.loader import render_to_string


def export_to_excel(filename, headers, rows):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Export'
    ws.append(headers)
    for row in rows:
        ws.append(row)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def export_to_pdf(request, template_name, context, filename):
    html = render_to_string(template_name, context, request=request)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=result)
    if pisa_status.err:
        return HttpResponse('Could not generate PDF.', status=500)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
