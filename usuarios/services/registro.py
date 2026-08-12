from django.db import transaction
from django.utils import timezone

from usuarios.models import Aprendiz, Rol, Usuario


@transaction.atomic
def registrar_aprendiz(*, tipo_documento, numero_documento, nombres, apellidos, email, password, ficha):
    """
    Crea el Usuario y su perfil de Aprendiz de forma atómica.
    Si algo falla, no queda ningún registro a medias.
    """

    rol_aprendiz, _ = Rol.objects.get_or_create(
        nombre="aprendiz",
        defaults={"descripcion": "Aprendiz en formación"}
    )

    usuario = Usuario.objects.create_user(
        numero_documento=numero_documento,
        password=password,
        tipo_documento=tipo_documento,
        nombres=nombres,
        apellidos=apellidos,
        email=email,
        rol=rol_aprendiz,
    )

    aprendiz = Aprendiz.objects.create(
        usuario=usuario,
        ficha=ficha,
        fecha_ingreso=timezone.now().date(),
    )

    return usuario, aprendiz
