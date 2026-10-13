import os

import httpx

from app.models import Projeto, PreferenciaTopico


BASE_URL = os.getenv(
    "JAVA_API_BASE_URL",
    "http://localhost:8080",
)

PROJETOS_PATH = os.getenv(
    "JAVA_API_PROJETOS_PATH",
    "/api/projetos",
)

PREFERENCIAS_PATH = os.getenv(
    "JAVA_API_PREFERENCIAS_PATH",
    "/api/usuarios/{usuario_id}/preferencias",
)


def extrair_lista(dados):
    if isinstance(dados, list):
        return dados

    if isinstance(dados, dict):
        for campo in ("content", "dados", "resultados"):
            if isinstance(dados.get(campo), list):
                return dados[campo]

    raise ValueError("A API Java não retornou uma lista válida.")


def normalizar_projeto(dados: dict) -> Projeto:
    topicos = dados.get("topicos", [])

    if not topicos:
        topicos = dados.get("projetoTopicos", [])

    nomes_topicos = []

    for item in topicos:
        if isinstance(item, str):
            nomes_topicos.append(item)
        elif isinstance(item, dict):
            topico = item.get("topico", item)
            if isinstance(topico, dict) and topico.get("nome"):
                nomes_topicos.append(topico["nome"])

    campos = {
        campo: dados[campo]
        for campo in Projeto.model_fields
        if campo in dados and campo != "topicos"
    }

    campos["topicos"] = nomes_topicos

    return Projeto(**campos)


def normalizar_preferencia(dados: dict) -> PreferenciaTopico | None:
    topico = dados.get("topico", "")

    if isinstance(topico, dict):
        topico = topico.get("nome", "")

    if not topico:
        return None

    return PreferenciaTopico(
        topico=str(topico),
        peso=float(dados.get("peso", 0)),
    )


async def buscar_dados(usuario_id: int):
    url_preferencias = PREFERENCIAS_PATH.format(
        usuario_id=usuario_id
    )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=15.0,
    ) as cliente:
        resposta_projetos = await cliente.get(PROJETOS_PATH)
        resposta_projetos.raise_for_status()

        resposta_preferencias = await cliente.get(
            url_preferencias
        )
        resposta_preferencias.raise_for_status()

    projetos = [
        normalizar_projeto(item)
        for item in extrair_lista(resposta_projetos.json())
    ]

    preferencias = [
        preferencia
        for item in extrair_lista(resposta_preferencias.json())
        if (preferencia := normalizar_preferencia(item)) is not None
    ]

    return projetos, preferencias