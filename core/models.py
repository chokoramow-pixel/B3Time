from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):

    # ---------- Información de autenticación ----------

    tipo_documento = models.CharField(
        max_length=5
    )

    numero_documento = models.CharField(
        max_length=20,
        unique=True
    )

    # ---------- Estados ----------

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    # ---------- Fechas ----------

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    # ---------- Manager ----------

    objects = UsuarioManager()

    # ---------- Login ----------

    USERNAME_FIELD = "numero_documento"

    REQUIRED_FIELDS = ["tipo_documento"]

    def __str__(self):
        return f"{self.tipo_documento} {self.numero_documento}"