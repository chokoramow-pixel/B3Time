from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from usuarios.forms import (
    LoginForm,
    RegistroAprendizForm,
    ProgramaFormacionForm,
    JornadaForm,
    FichaForm,
    AprendizEstadoForm,
)
from usuarios.decorators import administrador_requerido, personal_bienestar_requerido
from usuarios.mixins import AdministradorRequeridoMixin, PersonalBienestarRequeridoMixin
from usuarios.models import Aprendiz, Ficha, Jornada, ProgramaFormacion
from usuarios.services import registrar_aprendiz
from core.services.exportar import exportar_excel, exportar_word, exportar_pdf


def fichas_por_programa(request):
    """
    Devuelve en JSON las fichas activas de un programa de formación.
    La usa el <select> de fichas del formulario de registro para
    filtrarse dinámicamente según el programa elegido.
    """

    programa_id = request.GET.get("programa_formacion")

    if not programa_id:
        return JsonResponse([], safe=False)

    fichas = Ficha.objects.filter(
        programa_formacion_id=programa_id,
        estado="activa"
    ).order_by("numero_ficha").values(
        "id", "numero_ficha", jornada_nombre=F("jornada__nombre")
    )

    return JsonResponse(list(fichas), safe=False)


def registro_aprendiz(request):

    if request.user.is_authenticated:
        return redirect("usuarios:dashboard")

    form = RegistroAprendizForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        usuario, aprendiz = registrar_aprendiz(
            tipo_documento=form.cleaned_data["tipo_documento"],
            numero_documento=form.cleaned_data["numero_documento"],
            nombres=form.cleaned_data["nombres"],
            apellidos=form.cleaned_data["apellidos"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            ficha=form.cleaned_data["ficha"],
        )

        login(request, usuario)
        messages.success(request, "¡Tu cuenta se creó correctamente! Bienvenido a Be Time.")
        return redirect("usuarios:dashboard")

    return render(request, "usuarios/registro.html", {"form": form})


def login_view(request):

    if request.user.is_authenticated:
        return redirect("usuarios:dashboard")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        numero_documento = form.cleaned_data["numero_documento"]
        password = form.cleaned_data["password"]

        usuario = authenticate(
            request,
            username=numero_documento,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect("usuarios:dashboard")

        messages.error(request, "Documento o contraseña incorrectos.")

    return render(request, "usuarios/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("index")


@login_required(login_url="usuarios:login")
def dashboard_redirect(request):

    usuario = request.user

    if hasattr(usuario, "administrador"):
        return redirect("usuarios:dashboard_admin")

    if hasattr(usuario, "personal_bienestar"):
        return redirect("usuarios:dashboard_bienestar")

    if hasattr(usuario, "aprendiz"):
        return redirect("usuarios:dashboard_aprendiz")

    messages.warning(
        request,
        "Tu cuenta no tiene un perfil asignado todavía. Contacta al administrador."
    )
    logout(request)
    return redirect("usuarios:login")


@login_required(login_url="usuarios:login")
def dashboard_aprendiz(request):

    if not hasattr(request.user, "aprendiz"):
        return redirect("usuarios:dashboard")

    return render(request, "dashboard/aprendiz.html", {
        "aprendiz": request.user.aprendiz,
    })


@login_required(login_url="usuarios:login")
def dashboard_bienestar(request):

    if not hasattr(request.user, "personal_bienestar"):
        return redirect("usuarios:dashboard")

    return render(request, "dashboard/bienestar.html", {
        "personal_bienestar": request.user.personal_bienestar,
    })


@login_required(login_url="usuarios:login")
def dashboard_admin(request):

    if not hasattr(request.user, "administrador"):
        return redirect("usuarios:dashboard")

    return render(request, "dashboard/admin.html", {
        "administrador": request.user.administrador,
    })


# ==========================================================
# Panel de catálogos: Programas de Formación, Jornadas,
# Fichas y Aprendices.
# ==========================================================

# ---------- Programas de Formación (solo Administrador) ----------

class ProgramaFormacionListView(AdministradorRequeridoMixin, ListView):
    model = ProgramaFormacion
    template_name = "usuarios/programas_list.html"
    context_object_name = "programas"
    ordering = ["nombre"]


class ProgramaFormacionCreateView(AdministradorRequeridoMixin, CreateView):
    model = ProgramaFormacion
    form_class = ProgramaFormacionForm
    template_name = "usuarios/panel_form.html"
    success_url = reverse_lazy("usuarios:programas_lista")
    extra_context = {
        "titulo_pagina": "Crear programa de formación",
        "url_cancelar": reverse_lazy("usuarios:programas_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Programa de formación creado correctamente.")
        return super().form_valid(form)


class ProgramaFormacionUpdateView(AdministradorRequeridoMixin, UpdateView):
    model = ProgramaFormacion
    form_class = ProgramaFormacionForm
    template_name = "usuarios/panel_form.html"
    success_url = reverse_lazy("usuarios:programas_lista")
    extra_context = {
        "titulo_pagina": "Editar programa de formación",
        "url_cancelar": reverse_lazy("usuarios:programas_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Programa de formación actualizado correctamente.")
        return super().form_valid(form)


class ProgramaFormacionDeleteView(AdministradorRequeridoMixin, DeleteView):
    model = ProgramaFormacion
    template_name = "usuarios/panel_confirmar_eliminar.html"
    success_url = reverse_lazy("usuarios:programas_lista")
    extra_context = {
        "titulo_pagina": "Eliminar programa de formación",
        "url_cancelar": reverse_lazy("usuarios:programas_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Programa de formación eliminado.")
        return super().form_valid(form)


# ---------- Jornadas (solo Administrador) ----------

class JornadaListView(AdministradorRequeridoMixin, ListView):
    model = Jornada
    template_name = "usuarios/jornadas_list.html"
    context_object_name = "jornadas"
    ordering = ["nombre"]


class JornadaCreateView(AdministradorRequeridoMixin, CreateView):
    model = Jornada
    form_class = JornadaForm
    template_name = "usuarios/panel_form.html"
    success_url = reverse_lazy("usuarios:jornadas_lista")
    extra_context = {
        "titulo_pagina": "Crear jornada",
        "url_cancelar": reverse_lazy("usuarios:jornadas_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Jornada creada correctamente.")
        return super().form_valid(form)


class JornadaUpdateView(AdministradorRequeridoMixin, UpdateView):
    model = Jornada
    form_class = JornadaForm
    template_name = "usuarios/panel_form.html"
    success_url = reverse_lazy("usuarios:jornadas_lista")
    extra_context = {
        "titulo_pagina": "Editar jornada",
        "url_cancelar": reverse_lazy("usuarios:jornadas_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Jornada actualizada correctamente.")
        return super().form_valid(form)


class JornadaDeleteView(AdministradorRequeridoMixin, DeleteView):
    model = Jornada
    template_name = "usuarios/panel_confirmar_eliminar.html"
    success_url = reverse_lazy("usuarios:jornadas_lista")
    extra_context = {
        "titulo_pagina": "Eliminar jornada",
        "url_cancelar": reverse_lazy("usuarios:jornadas_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Jornada eliminada.")
        return super().form_valid(form)


# ---------- Fichas (Personal de Bienestar o Administrador) ----------

class FichaListView(PersonalBienestarRequeridoMixin, ListView):
    model = Ficha
    template_name = "usuarios/fichas_list.html"
    context_object_name = "fichas"

    def get_queryset(self):
        return Ficha.objects.select_related(
            "programa_formacion", "jornada"
        ).order_by("-fecha_creacion")


class FichaCreateView(PersonalBienestarRequeridoMixin, CreateView):
    model = Ficha
    form_class = FichaForm
    template_name = "usuarios/panel_form.html"
    success_url = reverse_lazy("usuarios:fichas_lista")
    extra_context = {
        "titulo_pagina": "Crear ficha",
        "url_cancelar": reverse_lazy("usuarios:fichas_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Ficha creada correctamente.")
        return super().form_valid(form)


class FichaUpdateView(PersonalBienestarRequeridoMixin, UpdateView):
    model = Ficha
    form_class = FichaForm
    template_name = "usuarios/panel_form.html"
    success_url = reverse_lazy("usuarios:fichas_lista")
    extra_context = {
        "titulo_pagina": "Editar ficha",
        "url_cancelar": reverse_lazy("usuarios:fichas_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Ficha actualizada correctamente.")
        return super().form_valid(form)


class FichaDeleteView(PersonalBienestarRequeridoMixin, DeleteView):
    model = Ficha
    template_name = "usuarios/panel_confirmar_eliminar.html"
    success_url = reverse_lazy("usuarios:fichas_lista")
    extra_context = {
        "titulo_pagina": "Eliminar ficha",
        "url_cancelar": reverse_lazy("usuarios:fichas_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Ficha eliminada.")
        return super().form_valid(form)


# ---------- Aprendices (Personal de Bienestar o Administrador) ----------
# Se crean por auto-registro; aquí solo se consultan y se reasigna
# su ficha/estado (activo, retirado, egresado). No se crean ni se
# eliminan desde este panel.

class AprendizListView(PersonalBienestarRequeridoMixin, ListView):
    model = Aprendiz
    template_name = "usuarios/aprendices_list.html"
    context_object_name = "aprendices"

    def get_queryset(self):
        return Aprendiz.objects.select_related(
            "usuario", "ficha", "ficha__programa_formacion"
        ).order_by("usuario__apellidos", "usuario__nombres")


class AprendizUpdateView(PersonalBienestarRequeridoMixin, UpdateView):
    model = Aprendiz
    form_class = AprendizEstadoForm
    template_name = "usuarios/panel_form.html"
    success_url = reverse_lazy("usuarios:aprendices_lista")
    extra_context = {
        "titulo_pagina": "Editar aprendiz",
        "url_cancelar": reverse_lazy("usuarios:aprendices_lista"),
    }

    def form_valid(self, form):
        messages.success(self.request, "Aprendiz actualizado correctamente.")
        return super().form_valid(form)


# ---------- Exportar catálogos (Excel / Word / PDF) ----------

def _responder_export(request, nombre_archivo, titulo, encabezados, filas):
    formato = request.GET.get("formato")

    if formato == "excel":
        return exportar_excel(nombre_archivo, titulo, encabezados, filas)
    if formato == "word":
        return exportar_word(nombre_archivo, titulo, encabezados, filas)
    if formato == "pdf":
        return exportar_pdf(nombre_archivo, titulo, encabezados, filas)

    messages.error(request, "Formato de exportación no válido.")
    return redirect("usuarios:dashboard")


@administrador_requerido
def exportar_programas(request):
    programas = ProgramaFormacion.objects.order_by("nombre")

    encabezados = ["Nombre", "Código", "Nivel", "Duración (meses)", "Estado"]
    filas = [
        [p.nombre, p.codigo, p.nivel_formacion, p.duracion_meses, p.estado]
        for p in programas
    ]

    return _responder_export(request, "programas_formacion", "Programas de formación", encabezados, filas)


@administrador_requerido
def exportar_jornadas(request):
    jornadas = Jornada.objects.order_by("nombre")

    encabezados = ["Nombre"]
    filas = [[j.nombre] for j in jornadas]

    return _responder_export(request, "jornadas", "Jornadas", encabezados, filas)


@personal_bienestar_requerido
def exportar_fichas(request):
    fichas = Ficha.objects.select_related("programa_formacion", "jornada").order_by("-fecha_creacion")

    encabezados = ["Número de ficha", "Programa", "Jornada", "Fecha inicio", "Fecha fin", "Estado"]
    filas = [
        [f.numero_ficha, f.programa_formacion.nombre, f.jornada.nombre, f.fecha_inicio, f.fecha_fin, f.estado]
        for f in fichas
    ]

    return _responder_export(request, "fichas", "Fichas", encabezados, filas)


@personal_bienestar_requerido
def exportar_aprendices(request):
    aprendices = Aprendiz.objects.select_related(
        "usuario", "ficha", "ficha__programa_formacion"
    ).order_by("usuario__apellidos", "usuario__nombres")

    encabezados = ["Nombres", "Apellidos", "Documento", "Ficha", "Programa", "Estado"]
    filas = [
        [
            a.usuario.nombres,
            a.usuario.apellidos,
            a.usuario.numero_documento,
            a.ficha.numero_ficha,
            a.ficha.programa_formacion.nombre,
            a.estado,
        ]
        for a in aprendices
    ]

    return _responder_export(request, "aprendices", "Aprendices", encabezados, filas)
