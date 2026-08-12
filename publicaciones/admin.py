from django.contrib import admin

from publicaciones.models import Publicacion
from usuarios.models import Usuario


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "autor", "estado", "fecha_publicacion")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Una publicación la escribe Bienestar o un administrador, nunca un aprendiz.
        if db_field.name == "autor":
            kwargs["queryset"] = Usuario.objects.exclude(
                aprendiz__isnull=False
            ).order_by("apellidos", "nombres")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
