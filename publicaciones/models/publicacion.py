from django.db import models


class Publicacion(models.Model):

    id = models.BigAutoField(primary_key=True)

    # ---------- Relaciones ----------

    autor = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.PROTECT,
        related_name="publicaciones"
    )

    # ---------- Información general ----------

    titulo = models.CharField(
        max_length=150
    )

    contenido = models.TextField()

    imagen = models.ImageField(
        upload_to="publicaciones/",
        null=True,
        blank=True
    )

    # ---------- Estados ----------

    estado = models.CharField(
        max_length=20,
        default="borrador"
    )

    # ---------- Fechas ----------

    fecha_publicacion = models.DateTimeField(
        null=True,
        blank=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"

    def __str__(self):
        return self.titulo
