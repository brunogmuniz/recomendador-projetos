from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import Projeto, PreferenciaTopico, Recomendacao


def texto_projeto(projeto: Projeto) -> str:
    campos = [
        projeto.titulo,
        projeto.resumo or "",
        projeto.classificacaoCNPQ or "",
        projeto.linhaPesquisa or "",
        projeto.tipoOrientacao or "",
        " ".join(projeto.topicos),
    ]

    return " ".join(campos).strip()


def recomendar_por_conteudo(
    projetos: list[Projeto],
    preferencias: list[PreferenciaTopico],
    limite: int = 10,
) -> list[Recomendacao]:
    if not projetos or not preferencias:
        return []

    preferencias_validas = [
        preferencia
        for preferencia in preferencias
        if preferencia.topico.strip() and preferencia.peso > 0
    ]

    soma_pesos = sum(
        preferencia.peso
        for preferencia in preferencias_validas
    )

    if soma_pesos <= 0:
        return []

    documentos = [
        texto_projeto(projeto)
        for projeto in projetos
    ]

    topicos_usuario = [
        preferencia.topico
        for preferencia in preferencias_validas
    ]

    try:
        vetorizar = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
        )

        matriz = vetorizar.fit_transform(
            documentos + topicos_usuario
        )
    except ValueError:
        return []

    quantidade_projetos = len(projetos)

    matriz_projetos = matriz[:quantidade_projetos]
    matriz_preferencias = matriz[quantidade_projetos:]

    similaridades = cosine_similarity(
        matriz_preferencias,
        matriz_projetos,
    )

    recomendacoes = []

    for indice, projeto in enumerate(projetos):
        pontuacao = sum(
            similaridades[indice_preferencia, indice]
            * preferencia.peso
            for indice_preferencia, preferencia
            in enumerate(preferencias_validas)
        ) / soma_pesos

        recomendacoes.append(
            Recomendacao(
                projeto=projeto,
                pontuacao=round(float(pontuacao), 4),
            )
        )

    recomendacoes.sort(
        key=lambda recomendacao: recomendacao.pontuacao,
        reverse=True,
    )

    return recomendacoes[:limite]