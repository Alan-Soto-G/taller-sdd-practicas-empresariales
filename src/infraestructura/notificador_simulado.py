"""Adaptador de correo simulado que implementa Notificador (sustituye al Servicio de correo institucional en esta etapa; ADR-007)."""

from aplicacion.errores.correo_no_enviado import CorreoNoEnviado


class NotificadorSimulado:
    """Guarda los correos enviados y, si el servicio no esta disponible, los deja pendientes de reenvio."""

    def __init__(self) -> None:
        self.disponible: bool = True
        self._enviados: list[dict[str, object]] = []
        self._pendientes: list[dict[str, object]] = []

    def enviar(self, destinatarios: list[str], asunto: str, mensaje: str) -> None:
        """Envia un correo o lo encola como pendiente si el servicio no esta disponible."""
        correo: dict[str, object] = {
            "destinatarios": list(destinatarios),
            "asunto": asunto,
            "mensaje": mensaje,
        }
        if self.disponible:
            self._enviados.append(correo)
        else:
            self._pendientes.append(correo)
            raise CorreoNoEnviado()

    def listar_enviados(self) -> list[dict[str, object]]:
        """Retorna una copia de los correos enviados."""
        return list(self._enviados)

    def listar_pendientes(self) -> list[dict[str, object]]:
        """Retorna una copia de los correos pendientes de reenvio."""
        return list(self._pendientes)
