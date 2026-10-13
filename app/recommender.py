from app.models import Projeto, PreferenciaTopico, Recomendacao
from app.services.content_based import recomendar_por_conteudo


def recomendar(
    projetos: list[Projeto],
    preferencias: list[PreferenciaTopico],
    limite: int = 10,
) -> list[Recomendacao]:
    return recomendar_por_conteudo(
        projetos=projetos,
        preferencias=preferencias,
        limite=limite,
    )