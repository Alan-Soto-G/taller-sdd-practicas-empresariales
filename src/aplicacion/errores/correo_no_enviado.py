"""Error: el Servicio de correo no pudo enviar la notificacion; queda pendiente de reenvio (ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class CorreoNoEnviado(ErrorAplicacion):
    def __init__(self) -> None:
        super().__init__("correo_no_enviado", "correo no enviado")
