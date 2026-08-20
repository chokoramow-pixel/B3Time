from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from bienestar.services import registrar_asistencia_y_horas
from core.services.exportar import responder_export
from eventos.forms import EventoForm
from eventos.models import Evento, Inscripcion
from usuarios.decorators import personal_bienestar_requerido
from usuarios.mixins import PersonalBienestarRequeridoMixin


def lista_eventos(request):

    eventos = Evento.objects.filter(
        fecha_inicio__gte=timezone.now()
    ).order_by("fecha_inicio")

    return render(request, "eventos/lista.html", {
        "eventos": eventos,
    })


def detalle_evento(request, evento_id):

    evento = get_object_or_404(Evento, id=evento_id)

    ya_inscrito = False
    if request.user.is_authenticated and hasattr(request.user, "aprendiz"):
        ya_inscrito = Inscripcion.objects.filter(
            evento=evento, aprendiz=request.user.aprendiz
        ).exclude(estado="cancelada").exists()

    return render(request, "eventos/detalle.html", {
        "evento": evento,
        "ya_inscrito": ya_inscrito,
    })


@login_required(login_url="usuarios:login")
def inscribirse_evento(request, evento_id):

    evento = get_object_or_404(Evento, id=evento_id)

    if not hasattr(request.user, "aprendiz"):
        messages.error(request, "Solo los aprendices pueden inscribirse a eventos.")
        return redirect("eventos:detalle", evento_id=evento.id)

    if evento.estado != "programado":
        messages.error(request, "Este evento ya no está abierto para inscripciones.")
        return redirect("eventos:detalle", evento_id=evento.id)

    if request.method == "POST":
        _, creada = Inscripcion.objects.get_or_create(
            evento=evento,
            aprendiz=request.user.aprendiz,
            defaults={"estado": "inscrito"},
        )

        if creada:
            messages.success(request, "Te inscribiste correctamente. ¡Nos vemos en el evento!")
        else:
            messages.info(request, "Ya estabas inscrito a este evento.")

    return redirect("eventos:detalle", evento_id=evento.id)


# ---------- Panel de gestión (Personal de Bienestar / Administrador) ----------
# CRUD como Class-Based Views, igual que ProgramaFormacion/Jornada/Ficha en usuarios.

class EventoListView(PersonalBienestarRequeridoMixin, ListView):
    model = Evento
    template_name = "eventos/panel_lista.html"
    context_object_name = "eventos"
    ordering = ["-fecha_inicio"]
    paginate_by = 15


class EventoCreateView(PersonalBienestarRequeridoMixin, CreateView):
    model = Evento
    form_class = EventoForm
    template_name = "eventos/form.html"
    success_url = reverse_lazy("eventos:panel_lista")
    extra_context = {"titulo_pagina": "Crear evento"}

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, "Evento creado correctamente.")
        return super().form_valid(form)


class EventoUpdateView(PersonalBienestarRequeridoMixin, UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = "eventos/form.html"
    success_url = reverse_lazy("eventos:panel_lista")
    extra_context = {"titulo_pagina": "Editar evento"}

    def form_valid(self, form):
        messages.success(self.request, "Evento actualizado correctamente.")
        return super().form_valid(form)


class EventoDeleteView(PersonalBienestarRequeridoMixin, DeleteView):
    model = Evento
    template_name = "eventos/confirmar_eliminar.html"
    context_object_name = "evento"
    success_url = reverse_lazy("eventos:panel_lista")

    def form_valid(self, form):
        messages.success(self.request, "Evento eliminado.")
        return super().form_valid(form)


@personal_bienestar_requerido
def exportar_eventos(request):
    eventos = Evento.objects.order_by("-fecha_inicio")

    q = request.GET.get("q", "").strip()
    if q:
        eventos = eventos.filter(Q(titulo__icontains=q) | Q(lugar__icontains=q))

    estado = request.GET.get("estado", "").strip()
    if estado:
        eventos = eventos.filter(estado=estado)

    encabezados = ["Título", "Lugar", "Fecha inicio", "Fecha fin", "Horas", "Estado", "Creado por"]
    filas = [
        [
            e.titulo, e.lugar, e.fecha_inicio, e.fecha_fin,
            e.horas_otorgadas, e.estado, e.creado_por.get_full_name(),
        ]
        for e in eventos
    ]

    return responder_export(request, "eventos", "Eventos", encabezados, filas, "eventos:panel_lista")


# ---------- Checklist de asistencia y horas de bienestar ----------
# El "checklist manual" del que habla el roadmap: Bienestar entra a un
# evento, ve a todos los inscritos, marca quién asistió y con cuántas
# horas -- todo en una sola pantalla. Solo Personal de Bienestar puede
# ENVIAR el checklist (asignar horas), aunque Administrador también
# puede entrar a mirarlo, porque HorasBienestar.asignado_por solo
# acepta un PersonalBienestar, no un Administrador (así quedó
# diseñado el modelo desde el principio).

@personal_bienestar_requerido
def checklist_inscritos(request, evento_id):

    evento = get_object_or_404(Evento, id=evento_id)

    inscripciones = Inscripcion.objects.filter(
        evento=evento
    ).exclude(
        estado="cancelada"
    ).select_related(
        "aprendiz__usuario", "asistencia"
    ).order_by("aprendiz__usuario__apellidos", "aprendiz__usuario__nombres")

    if request.method == "POST":

        if not hasattr(request.user, "personal_bienestar"):
            messages.error(
                request,
                "Solo Personal de Bienestar puede otorgar horas (un Administrador "
                "puede ver este checklist, pero no enviarlo)."
            )
            return redirect("eventos:panel_inscritos", evento_id=evento.id)

        for inscripcion in inscripciones:
            asistio = request.POST.get(f"asistio_{inscripcion.id}") == "on"
            horas_texto = request.POST.get(f"horas_{inscripcion.id}", "").strip()
            cantidad_horas = int(horas_texto) if horas_texto.isdigit() else 0

            registrar_asistencia_y_horas(
                inscripcion=inscripcion,
                asistio=asistio,
                cantidad_horas=cantidad_horas,
                motivo=f"Asistencia a: {evento.titulo}",
                asignado_por=request.user.personal_bienestar,
            )

        messages.success(request, "Asistencia y horas registradas correctamente.")
        return redirect("eventos:panel_inscritos", evento_id=evento.id)

    return render(request, "eventos/checklist_inscritos.html", {
        "evento": evento,
        "inscripciones": inscripciones,
    })
