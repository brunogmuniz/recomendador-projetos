from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import Projeto, PreferenciaTopico, Recomendacao


def limpar_valor(valor: str | None) -> str:
    if not valor:
        return ""

    valor = valor.strip()

    placeholders = {
        "não informado",
        "[não informado]",
        "nao informado",
        "[nao informado]",
        "não informada",
        "[não informada]",
        "nao informada",
        "[nao informada]",
        "não informado(a)",
        "[não informado(a)]",
    }

    if valor.casefold() in placeholders:
        return ""

    return valor



def texto_projeto(projeto: Projeto) -> str:
    campos = [
        limpar_valor(projeto.titulo),
        limpar_valor(projeto.resumo),
        limpar_valor(projeto.classificacaoCNPQ),
        limpar_valor(projeto.linhaPesquisa),
        limpar_valor(projeto.tipoOrientacao),
    ]

    topicos = [
        limpar_valor(topico)
        for topico in projeto.topicos
    ]

    campos.extend(topico for topico in topicos if topico)

    return " ".join(campo for campo in campos if campo).strip()


def selecionar_com_diversidade(
    similaridades,
    preferencias: list[PreferenciaTopico],
    recomendacoes: list[Recomendacao],
    limite: int,
) -> list[Recomendacao]:
    candidatos = [
        [
            int(indice)
            for indice in similaridades[i].argsort()[::-1]
            if similaridades[i, indice] > 0
        ]
        for i in range(len(preferencias))
    ]

    posicao = [0] * len(preferencias)
    escolhidos_por_preferencia = [0] * len(preferencias)
    selecionados: list[int] = []
    usados: set[int] = set()

    while len(selecionados) < limite:
        ordem = sorted(
            range(len(preferencias)),
            key=lambda i: preferencias[i].peso / (escolhidos_por_preferencia[i] + 1),
            reverse=True,
        )

        escolhida = None
        for i in ordem:
            while posicao[i] < len(candidatos[i]) and candidatos[i][posicao[i]] in usados:
                posicao[i] += 1
            if posicao[i] < len(candidatos[i]):
                escolhida = i
                break

        if escolhida is None:
            break

        indice = candidatos[escolhida][posicao[escolhida]]
        usados.add(indice)
        selecionados.append(indice)
        escolhidos_por_preferencia[escolhida] += 1

    if len(selecionados) < limite:
        ranking = sorted(
            range(len(recomendacoes)),
            key=lambda i: recomendacoes[i].pontuacao,
            reverse=True,
        )
        for indice in ranking:
            if len(selecionados) >= limite:
                break
            if indice not in usados:
                usados.add(indice)
                selecionados.append(indice)

    return [recomendacoes[indice] for indice in selecionados]


def recomendar_por_conteudo(
    projetos: list[Projeto],
    preferencias: list[PreferenciaTopico],
    limite: int = 10,
) -> list[Recomendacao]:

    print(f"[RECOMENDACAO] Projetos recebidos: {len(projetos)}")
    print(f"[RECOMENDACAO] Preferências recebidas: {len(preferencias)}")
    if not projetos:
        return []

    if not preferencias:
        projetos_recentes = sorted(
            projetos,
            key=lambda projeto: projeto.dataInicio or "",
            reverse=True,
        )

        return [
            Recomendacao(projeto=projeto, pontuacao=0.0)
            for projeto in projetos_recentes[:limite]
        ]

    
    preferencias_validas = [
        preferencia
        for preferencia in preferencias
        if (
          limpar_valor(preferencia.topico)
         and preferencia.peso > 0
        )
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

    return selecionar_com_diversidade(
        similaridades,
        preferencias_validas,
        recomendacoes,
        limite,
    )