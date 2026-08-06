from django.db import models


class Rol(models.Model):

    id = models.BigAutoField(primary_key=True)

    # ---------- Información general ----------

    nombre = models.CharField(
        max_length=50,
        unique=True
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True
    )

    # ---------- Fechas ----------

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.nombre
