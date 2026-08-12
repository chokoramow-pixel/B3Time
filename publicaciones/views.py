from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.services.exportar import exportar_excel, exportar_word, exportar_pdf
from publicaciones.forms import PublicacionForm
from publicaciones.models import Publicacion
from usuarios.decorators import personal_bienestar_requerido


def lista_publicaciones(request):

    publicaciones = Publicacion.objects.filter(
        estado="publicado"
    ).order_by("-fecha_publicacion")

    return render(request, "publicaciones/lista.html", {
        "publicaciones": publicaciones,
    })


def detalle_publicacion(request, publicacion_id):

    publicacion = get_object_or_404(
        Publicacion,
        id=publicacion_id,
        estado="publicado"
    )

    return render(request, "publicaciones/detalle.html", {
        "publicacion": publicacion,
    })


# ---------- Panel de gestión (Personal de Bienestar / Administrador) ----------

@personal_bienestar_requerido
def panel_publicaciones(request):

    publicaciones = Publicacion.objects.order_by("-fecha_creacion")

    return render(request, "publicaciones/panel_lista.html", {
        "publicaciones": publicaciones,
    })


@personal_bienestar_requerido
def crear_publicacion(request):

    form = PublicacionForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        publicacion = form.save(commit=False)
        publicacion.autor = request.user

        if publicacion.estado == "publicado" and not publicacion.fecha_publicacion:
            publicacion.fecha_publicacion = timezone.now()

        publicacion.save()

        messages.success(request, "Publicación creada correctamente.")
        return redirect("publicaciones:panel_lista")

    return render(request, "publicaciones/form.html", {
        "form": form,
        "titulo_pagina": "Crear publicación",
    })


@personal_bienestar_requerido
def editar_publicacion(request, publicacion_id):

    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    form = PublicacionForm(request.POST or None, request.FILES or None, instance=publicacion)

    if request.method == "POST" and form.is_valid():
        publicacion = form.save(commit=False)

        if publicacion.estado == "publicado" and not publicacion.fecha_publicacion:
            publicacion.fecha_publicacion = timezone.now()

        publicacion.save()

        messages.success(request, "Publicación actualizada correctamente.")
        return redirect("publicaciones:panel_lista")

    return render(request, "publicaciones/form.html", {
        "form": form,
        "titulo_pagina": "Editar publicación",
    })


@personal_bienestar_requerido
def eliminar_publicacion(request, publicacion_id):

    publicacion = get_object_or_404(Publicacion, id=publicacion_id)

    if request.method == "POST":
        publicacion.delete()
        messages.success(request, "Publicación eliminada.")
        return redirect("publicaciones:panel_lista")

    return render(request, "publicaciones/confirmar_eliminar.html", {
        "publicacion": publicacion,
    })


@personal_bienestar_requerido
def exportar_publicaciones(request):
    publicaciones = Publicacion.objects.order_by("-fecha_creacion")

    encabezados = ["Título", "Autor", "Estado", "Fecha publicación"]
    filas = [
        [p.titulo, p.autor.get_full_name(), p.estado, p.fecha_publicacion]
        for p in publicaciones
    ]

    formato = request.GET.get("formato")
    if formato == "excel":
        return exportar_excel("publicaciones", "Publicaciones", encabezados, filas)
    if formato == "word":
        return exportar_word("publicaciones", "Publicaciones", encabezados, filas)
    if formato == "pdf":
        return exportar_pdf("publicaciones", "Publicaciones", encabezados, filas)

    messages.error(request, "Formato de exportación no válido.")
    return redirect("publicaciones:panel_lista")
