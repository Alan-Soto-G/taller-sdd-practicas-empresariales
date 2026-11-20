"""Caso de uso CU-13 (Modulo Configuracion): importa el historico de Excel ya leido; valida cada fila, carga las validas y reporta las rechazadas sin cargarlas en silencio (PA-07, S-04, ADR-004, ADR-006, ADR-008)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.configuracion.consultar_regla_vigente import ConsultarReglaVigente
from aplicacion.configuracion.fila_rechazada import FilaRechazada
from aplicacion.configuracion.resultado_importacion import ResultadoImportacion
from aplicacion.configuracion.solicitud_importacion import SolicitudImportacion
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from aplicacion.usuario_autenticado import UsuarioAutenticado
from dominio.correo import Correo
from dominio.empresa import Empresa
from dominio.estado_practica import EstadoPractica
from dominio.estudiante import Estudiante
from dominio.plaza import Plaza
from dominio.practica import Practica
from dominio.tutor import Tutor

ROL_COORDINADOR = "CoordinadorPracticas"
CAMPOS = {
    "Empresas": ("id", "razon_social"),
    "Plazas": ("id", "id_empresa", "cargo", "cupos", "periodo"),
    "Tutores": ("id", "correo"),
    "Estudiantes": ("id", "correo"),
    "Practicas": ("id", "id_estudiante", "id_empresa", "id_tutor"),
}
PRIMERA_FILA_DE_DATOS = 2  # la fila 1 del Excel es el encabezado


class ImportarHistorico:
    """Importador de una sola vez: procesa las hojas en orden para que cada fila pueda usar lo cargado antes."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        consultar_regla: ConsultarReglaVigente,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._consultar_regla = consultar_regla
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudImportacion) -> ResultadoImportacion:
        """Carga las filas validas y devuelve, por hoja, cuantas se cargaron y cuales se rechazaron y por que."""
        usuario = solicitud.usuario
        ahora = self._reloj()
        if usuario.rol != ROL_COORDINADOR:
            self._bitacora.registrar(usuario.id, usuario.rol, "importacion", "importar histórico", ahora)
            raise AccesoDenegado()

        rechazadas = [FilaRechazada(hoja, 1, "hoja desconocida") for hoja in solicitud.hojas if hoja not in CAMPOS]
        cargadas = {hoja: 0 for hoja in CAMPOS}
        version = self._consultar_regla.ejecutar().version
        for hoja, campos in CAMPOS.items():
            for indice, fila in enumerate(solicitud.hojas.get(hoja, [])):
                datos = {clave: str(valor).strip() for clave, valor in fila.items() if valor is not None}
                faltante = next((c for c in campos if not datos.get(c)), None)
                motivo = (
                    f"falta el campo {faltante}"
                    if faltante
                    else self._cargar(hoja, datos, version, usuario, ahora)
                )
                if motivo is None:
                    cargadas[hoja] += 1
                else:
                    rechazadas.append(FilaRechazada(hoja, indice + PRIMERA_FILA_DE_DATOS, motivo))

        self._bitacora.registrar(
            usuario.id,
            usuario.rol,
            "importacion",
            f"importar histórico: {sum(cargadas.values())} cargadas, {len(rechazadas)} rechazadas",
            ahora,
        )
        return ResultadoImportacion(cargadas, tuple(rechazadas))

    def _cargar(
        self, hoja: str, d: dict[str, str], version: str, usuario: UsuarioAutenticado, ahora: datetime
    ) -> str | None:
        """Valida y guarda una fila; devuelve el motivo del rechazo o None si se cargo."""
        repo = self._repositorio
        if hoja == "Empresas":
            if repo.obtener_empresa(d["id"]) is not None:
                return f"ya existe empresa {d['id']}"
            repo.guardar_empresa(Empresa(d["id"], d["razon_social"]))
            return None

        if hoja == "Plazas":
            if repo.obtener_plaza(d["id"]) is not None:
                return f"ya existe plaza {d['id']}"
            if repo.obtener_empresa(d["id_empresa"]) is None:
                return f"la empresa {d['id_empresa']} no existe"
            try:
                cupos = int(d["cupos"])
            except ValueError:
                return "los cupos deben ser un número entero"
            motivo = Plaza.motivo_invalidez(d["cargo"], cupos, d["periodo"])
            if motivo is not None:
                return motivo
            repo.guardar_plaza(Plaza(d["id"], d["id_empresa"], d["cargo"], cupos, d["periodo"]))
            return None

        if hoja in ("Tutores", "Estudiantes"):
            existente = repo.obtener_tutor(d["id"]) if hoja == "Tutores" else repo.obtener_estudiante(d["id"])
            entidad = "tutor" if hoja == "Tutores" else "estudiante"
            if existente is not None:
                return f"ya existe {entidad} {d['id']}"
            if not Correo.es_valido(d["correo"]):
                return "el correo no es válido"
            if hoja == "Tutores":
                repo.guardar_tutor(Tutor(d["id"], d["correo"]))
            else:
                repo.guardar_estudiante(Estudiante(d["id"], d["correo"]))
            return None

        if repo.obtener_practica(d["id"]) is not None:
            return f"ya existe práctica {d['id']}"
        if repo.obtener_estudiante(d["id_estudiante"]) is None:
            return f"el estudiante {d['id_estudiante']} no existe"
        if repo.obtener_empresa(d["id_empresa"]) is None:
            return f"la empresa {d['id_empresa']} no existe"
        if repo.obtener_tutor(d["id_tutor"]) is None:
            return f"el tutor {d['id_tutor']} no existe"
        repo.guardar_practica(
            Practica(d["id"], d["id_estudiante"], d["id_empresa"], version, EstadoPractica.EN_CURSO, d["id_tutor"])
        )  # practicas en curso con la regla vigente (PA-07, ADR-008)
        self._bitacora.registrar(
            usuario.id, usuario.rol, f"practica:{d['id']}", "crear con estado en curso por importación", ahora
        )
        return None
