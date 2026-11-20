"""Caso de uso CU-14 (Modulo Postulaciones): el Coordinador crea, lista, actualiza y elimina empresas aliadas y registra su representante (ADR-004, ADR-005, ADR-006, ADR-007)."""

from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.empresa_no_encontrada import EmpresaNoEncontrada
from aplicacion.errores.empresa_no_permitida import EmpresaNoPermitida
from aplicacion.errores.empresa_no_valida import EmpresaNoValida
from aplicacion.postulaciones.empresa_gestionada import EmpresaGestionada
from aplicacion.postulaciones.solicitud_empresa import SolicitudEmpresa
from aplicacion.postulaciones.solicitud_representante import SolicitudRepresentante
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from aplicacion.usuario_autenticado import UsuarioAutenticado
from dominio.empresa import Empresa
from dominio.representante_empresa import RepresentanteEmpresa

ROL_COORDINADOR = "CoordinadorPracticas"


class GestionarEmpresas:
    """CRUD de Empresa y registro de su RepresentanteEmpresa; solo el Coordinador."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._reloj = reloj

    def crear(self, solicitud: SolicitudEmpresa) -> EmpresaGestionada:
        """Registra una Empresa aliada nueva."""
        self._autorizar(solicitud.usuario, f"empresa:{solicitud.id_empresa}")
        self._validar_empresa(solicitud.razon_social, solicitud.nit)
        if not solicitud.id_empresa.strip():
            raise EmpresaNoValida("el id de la empresa es obligatorio")
        if self._repositorio.obtener_empresa(solicitud.id_empresa) is not None:
            raise EmpresaNoPermitida(f"ya existe empresa {solicitud.id_empresa}")
        empresa = Empresa(solicitud.id_empresa, solicitud.razon_social, solicitud.nit)
        self._repositorio.guardar_empresa(empresa)
        return self._a_dto(empresa)

    def actualizar(self, solicitud: SolicitudEmpresa) -> EmpresaGestionada:
        """Cambia la razon social y el NIT; conserva el id, las plazas y las practicas."""
        self._autorizar(solicitud.usuario, f"empresa:{solicitud.id_empresa}")
        self._existente(solicitud.id_empresa)
        self._validar_empresa(solicitud.razon_social, solicitud.nit)
        empresa = Empresa(solicitud.id_empresa, solicitud.razon_social, solicitud.nit)
        self._repositorio.guardar_empresa(empresa)
        return self._a_dto(empresa)

    def eliminar(self, solicitud: SolicitudEmpresa) -> None:
        """Elimina una Empresa solo si no tiene plazas ni practicas."""
        self._autorizar(solicitud.usuario, f"empresa:{solicitud.id_empresa}")
        self._existente(solicitud.id_empresa)
        con_plazas = any(p.id_empresa == solicitud.id_empresa for p in self._repositorio.listar_plazas())
        con_practicas = any(p.id_empresa == solicitud.id_empresa for p in self._repositorio.listar_practicas())
        if con_plazas or con_practicas:
            raise EmpresaNoPermitida("la empresa tiene plazas o prácticas")
        self._repositorio.eliminar_empresa(solicitud.id_empresa)

    def listar(self, usuario: UsuarioAutenticado) -> tuple[EmpresaGestionada, ...]:
        """Devuelve las Empresas ordenadas por id, con su representante."""
        self._autorizar(usuario, "empresas")
        empresas = sorted(self._repositorio.listar_empresas(), key=lambda e: e.id)
        return tuple(self._a_dto(empresa) for empresa in empresas)

    def registrar_representante(self, solicitud: SolicitudRepresentante) -> EmpresaGestionada:
        """Registra o actualiza el representante; a su correo llegan los enlaces nuevos (ADR-005)."""
        self._autorizar(solicitud.usuario, f"empresa:{solicitud.id_empresa}")
        empresa = self._existente(solicitud.id_empresa)
        motivo = RepresentanteEmpresa.motivo_invalidez(solicitud.nombre, solicitud.correo)
        if motivo is not None:
            raise EmpresaNoValida(motivo)
        actual = self._repositorio.obtener_representante_de_empresa(empresa.id)
        id_representante = actual.id if actual is not None else f"R-{uuid4().hex[:8]}"
        self._repositorio.guardar_representante(
            RepresentanteEmpresa(id_representante, empresa.id, solicitud.nombre, solicitud.correo)
        )
        return self._a_dto(empresa)

    def _autorizar(self, usuario: UsuarioAutenticado, recurso: str) -> None:
        """Solo el Coordinador; el rechazo se audita (ADR-004, ADR-006)."""
        if usuario.rol != ROL_COORDINADOR:
            self._bitacora.registrar(usuario.id, usuario.rol, recurso, "gestionar empresas", self._reloj())
            raise AccesoDenegado()

    def _existente(self, id_empresa: str) -> Empresa:
        """Devuelve la Empresa o lanza EmpresaNoEncontrada."""
        empresa = self._repositorio.obtener_empresa(id_empresa)
        if empresa is None:
            raise EmpresaNoEncontrada(id_empresa)
        return empresa

    def _validar_empresa(self, razon_social: str, nit: str) -> None:
        """Aplica la regla de la Empresa."""
        motivo = Empresa.motivo_invalidez(razon_social, nit)
        if motivo is not None:
            raise EmpresaNoValida(motivo)

    def _a_dto(self, empresa: Empresa) -> EmpresaGestionada:
        """Arma la salida con el representante actual de la Empresa."""
        representante = self._repositorio.obtener_representante_de_empresa(empresa.id)
        return EmpresaGestionada(
            empresa.id,
            empresa.razon_social,
            empresa.nit,
            representante.id if representante else None,
            representante.nombre if representante else None,
            representante.correo if representante else None,
        )
