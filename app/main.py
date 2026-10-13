from fastapi import FastAPI, HTTPException, Query
import httpx

from app.recommender import recomendar
from app.services.java_api import buscar_dados


app = FastAPI(
    title="Recomendador de Projetos UFSM",
    description="Recomendação de projetos acadêmicos baseada em conteúdo.",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/recommendations/{usuario_id}")
async def recomendacoes(
    usuario_id: int,
    limite: int = Query(default=10, ge=1, le=50),
):
    try:
        projetos, preferencias = await buscar_dados(usuario_id)

        resultados = recomendar(
            projetos=projetos,
            preferencias=preferencias,
            limite=limite,
        )

        return {
            "usuarioId": usuario_id,
            "quantidade": len(resultados),
            "recomendacoes": [
                resultado.model_dump()
                for resultado in resultados
            ],
        }

    except httpx.HTTPError as erro:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível consultar a API Java.",
        ) from erro

    except (ValueError, TypeError) as erro:
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível processar os dados do Java: {erro}",
        ) from erro
