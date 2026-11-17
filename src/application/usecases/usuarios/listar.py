from src.domain.entities.usuario import Usuario
from src.domain.repositories.usuario_repository import UsuarioRepository


class ListarUsuariosUseCase:
    def __init__(self, repositorio: UsuarioRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self) -> list[Usuario]:
        return self._repositorio.find_all()
