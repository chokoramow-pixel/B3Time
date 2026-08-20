from django.contrib import admin
from django.db import models

from bienestar.models import HorasBienestar, Asesoria
from core.widgets import AdminSplitDateTimeSinSegundos


@admin.register(HorasBienestar)
class HorasBienestarAdmin(admin.ModelAdmin):
    list_display = ("id", "asistencia", "cantidad_horas", "asignado_por", "fecha")


@admin.register(Asesoria)
class AsesoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo", "aprendiz", "personal_bienestar", "estado", "fecha_solicitud")
    formfield_overrides = {
        models.DateTimeField: {"widget": AdminSplitDateTimeSinSegundos},
    }
