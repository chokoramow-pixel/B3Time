"""
Utilidades compartidas para exportar cualquier listado del panel
(Programas, Jornadas, Fichas, Aprendices, Eventos, Publicaciones...)
a Excel, Word o PDF, sin duplicar la lógica en cada vista.

Uso típico dentro de una vista:

    from core.services.exportar import exportar_excel, exportar_word, exportar_pdf

    encabezados = ["Nombre", "Código", "Estado"]
    filas = [[p.nombre, p.codigo, p.estado] for p in programas]

    formato = request.GET.get("formato")
    if formato == "excel":
        return exportar_excel("programas", "Programas de formación", encabezados, filas)
    if formato == "word":
        return exportar_word("programas", "Programas de formación", encabezados, filas)
    if formato == "pdf":
        return exportar_pdf("programas", "Programas de formación", encabezados, filas)
"""

from io import BytesIO

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect


def responder_export(request, nombre_archivo, titulo, encabezados, filas, url_error):
    """
    Decide en qué formato responder (excel/word/pdf) según el parámetro
    ?formato= de la URL. Centraliza lo que antes cada app repetía a mano.

    url_error: nombre de la url (con namespace, ej. "eventos:panel_lista")
    a la que volver si el formato pedido no es válido.
    """
    formato = request.GET.get("formato")

    if formato == "excel":
        return exportar_excel(nombre_archivo, titulo, encabezados, filas)
    if formato == "word":
        return exportar_word(nombre_archivo, titulo, encabezados, filas)
    if formato == "pdf":
        return exportar_pdf(nombre_archivo, titulo, encabezados, filas)

    messages.error(request, "Formato de exportación no válido.")
    return redirect(url_error)


def _valor_a_texto(valor):
    if valor is None:
        return ""
    return str(valor)


def exportar_excel(nombre_archivo, titulo, encabezados, filas):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    libro = Workbook()
    hoja = libro.active
    hoja.title = titulo[:31] or "Datos"

    hoja.append(encabezados)
    for celda in hoja[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill(start_color="2E8B3D", end_color="2E8B3D", fill_type="solid")

    for fila in filas:
        hoja.append([_valor_a_texto(v) for v in fila])

    for columna in hoja.columns:
        ancho = max(len(_valor_a_texto(c.value)) for c in columna) + 2
        hoja.column_dimensions[columna[0].column_letter].width = min(ancho, 40)

    buffer = BytesIO()
    libro.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}.xlsx"'
    return response


def exportar_word(nombre_archivo, titulo, encabezados, filas):
    from docx import Document
    from docx.shared import Pt

    documento = Document()
    documento.add_heading(titulo, level=1)

    tabla = documento.add_table(rows=1, cols=len(encabezados))
    tabla.style = "Light Grid Accent 1"

    celdas_encabezado = tabla.rows[0].cells
    for i, encabezado in enumerate(encabezados):
        celdas_encabezado[i].text = encabezado
        for parrafo in celdas_encabezado[i].paragraphs:
            for run in parrafo.runs:
                run.font.bold = True

    for fila in filas:
        celdas = tabla.add_row().cells
        for i, valor in enumerate(fila):
            celdas[i].text = _valor_a_texto(valor)

    for parrafo in documento.paragraphs:
        for run in parrafo.runs:
            run.font.size = Pt(11)

    buffer = BytesIO()
    documento.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}.docx"'
    return response


def exportar_pdf(nombre_archivo, titulo, encabezados, filas):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

    buffer = BytesIO()
    documento = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    estilos = getSampleStyleSheet()

    elementos = [
        Paragraph(titulo, estilos["Title"]),
        Spacer(1, 12),
    ]

    datos_tabla = [encabezados] + [[_valor_a_texto(v) for v in fila] for fila in filas]
    tabla = Table(datos_tabla, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E8B3D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E1E9DC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F8F0")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla)

    documento.build(elementos)
    buffer.seek(0)

    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}.pdf"'
    return response
