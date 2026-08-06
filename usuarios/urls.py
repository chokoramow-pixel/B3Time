from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from usuarios import views
from usuarios.forms import RecuperarContrasenaForm, NuevaContrasenaForm

app_name = "usuarios"

urlpatterns = [
    path("registro/", views.registro_aprendiz, name="registro"),
    path("ajax/fichas/", views.fichas_por_programa, name="fichas_por_programa"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("dashboard/aprendiz/", views.dashboard_aprendiz, name="dashboard_aprendiz"),
    path("dashboard/bienestar/", views.dashboard_bienestar, name="dashboard_bienestar"),
    path("dashboard/admin/", views.dashboard_admin, name="dashboard_admin"),

    # ---------- Restablecer contraseña ----------

    path(
        "recuperar-contrasena/",
        auth_views.PasswordResetView.as_view(
            form_class=RecuperarContrasenaForm,
            template_name="usuarios/password_reset.html",
            email_template_name="usuarios/password_reset_email.html",
            subject_template_name="usuarios/password_reset_subject.txt",
            success_url=reverse_lazy("usuarios:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "recuperar-contrasena/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuarios/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "recuperar-contrasena/confirmar/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            form_class=NuevaContrasenaForm,
            template_name="usuarios/password_reset_confirm.html",
            success_url=reverse_lazy("usuarios:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "recuperar-contrasena/completado/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuarios/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
