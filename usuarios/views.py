from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from usuarios.forms import LoginForm, RegistroAprendizForm
from usuarios.models import Ficha
from usuarios.services import registrar_aprendiz


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
    ).order_by("numero_ficha").values("id", "numero_ficha", "jornada")

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
