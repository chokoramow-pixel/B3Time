from django.contrib.auth.base_user import BaseUserManager


class UsuarioManager(BaseUserManager):

    def create_user(self, numero_documento, password=None, **extra_fields):

        if not numero_documento:
            raise ValueError("El número de documento es obligatorio.")

        usuario = self.model(
            numero_documento=numero_documento,
            **extra_fields
        )

        usuario.set_password(password)

        usuario.save(using=self._db)

        return usuario


    def create_superuser(self, numero_documento, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            numero_documento,
            password,
            **extra_fields
        )