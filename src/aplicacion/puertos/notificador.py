"""Puerto para enviar correos y enlaces (glosario: Notificador; ADR-007). Lo implementa infraestructura."""

from typing import Protocol


class Notificador(Protocol):
    def enviar(self, destinatarios: list[str], asunto: str, mensaje: str) -> None:
        """Envia un correo; lanza CorreoNoEnviado si falla y lo deja pendiente de reenvio."""
        ...
