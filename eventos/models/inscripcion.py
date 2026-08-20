from django.db import models

ESTADO_CHOICES = [
    ("inscrito", "Inscrito"),
    ("asistio", "Asistió"),
    ("no_asistio", "No asistió"),
    ("cancelada", "Cancelada"),
]


class Inscripcion(models.Model):

    id = models.BigAutoField(primary_key=True)

    # ---------- Relaciones ----------

    evento = models.ForeignKey(
        "eventos.Evento",
        on_delete=models.CASCADE,
        related_name="inscripciones"
    )

    aprendiz = models.ForeignKey(
        "usuarios.Aprendiz",
        on_delete=models.CASCADE,
        related_name="inscripciones"
    )

    # ---------- Estados ----------

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="inscrito"
    )

    # ---------- Fechas ----------

    fecha_inscripcion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        unique_together = ("evento", "aprendiz")

    def __str__(self):
        return f"{self.aprendiz} - {self.evento}"
