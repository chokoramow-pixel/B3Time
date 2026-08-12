from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.services.exportar import exportar_excel, exportar_word, exportar_pdf
from eventos.forms import EventoForm
from eventos.models import Evento
from usuarios.decorators import personal_bienestar_requerido


def lista_eventos(request):

    eventos = Evento.objects.filter(
        fecha_inicio__gte=timezone.now()
    ).order_by("fecha_inicio")

    return render(request, "eventos/lista.html", {
        "eventos": eventos,
    })


def detalle_evento(request, evento_id):

    evento = get_object_or_404(Evento, id=evento_id)

    return render(request, "eventos/detalle.html", {
        "evento": evento,
    })


# ---------- Panel de gestión (Personal de Bienestar / Administrador) ----------

@personal_bienestar_requerido
def panel_eventos(request):

    eventos = Evento.objects.order_by("-fecha_inicio")

    return render(request, "eventos/panel_lista.html", {
        "eventos": eventos,
    })


@personal_bienestar_requerido
def crear_evento(request):

    form = EventoForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        evento = form.save(commit=False)
        evento.creado_por = request.user
        evento.save()

        messages.success(request, "Evento creado correctamente.")
        return redirect("eventos:panel_lista")

    return render(request, "eventos/form.html", {
        "form": form,
        "titulo_pagina": "Crear evento",
    })


@personal_bienestar_requerido
def editar_evento(request, evento_id):

    evento = get_object_or_404(Evento, id=evento_id)
    form = EventoForm(request.POST or None, request.FILES or None, instance=evento)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Evento actualizado correctamente.")
        return redirect("eventos:panel_lista")

    return render(request, "eventos/form.html", {
        "form": form,
        "titulo_pagina": "Editar evento",
    })


@personal_bienestar_requerido
def eliminar_evento(request, evento_id):

    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == "POST":
        evento.delete()
        messages.success(request, "Evento eliminado.")
        return redirect("eventos:panel_lista")

    return render(request, "eventos/confirmar_eliminar.html", {
        "evento": evento,
    })


@personal_bienestar_requerido
def exportar_eventos(request):
    eventos = Evento.objects.order_by("-fecha_inicio")

    encabezados = ["Título", "Lugar", "Fecha inicio", "Fecha fin", "Horas", "Estado", "Creado por"]
    filas = [
        [
            e.titulo, e.lugar, e.fecha_inicio, e.fecha_fin,
            e.horas_otorgadas, e.estado, e.creado_por.get_full_name(),
        ]
        for e in eventos
    ]

    formato = request.GET.get("formato")
    if formato == "excel":
        return exportar_excel("eventos", "Eventos", encabezados, filas)
    if formato == "word":
        return exportar_word("eventos", "Eventos", encabezados, filas)
    if formato == "pdf":
        return exportar_pdf("eventos", "Eventos", encabezados, filas)

    messages.error(request, "Formato de exportación no válido.")
    return redirect("eventos:panel_lista")
