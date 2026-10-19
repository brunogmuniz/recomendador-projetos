from fastapi import FastAPI, HTTPException, Query, Request
import httpx

from app.models import DadosRecomendacao
from app.recommender import recomendar
from app.services.java_api import buscar_dados


app = FastAPI(
    title="Recomendador de Projetos UFSM",
    description="Recomendação de projetos acadêmicos baseada em conteúdo.",
    version="0.2.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/debug-body")
async def debug_body(request: Request):
    body = await request.body()

    return {
        "content_type": request.headers.get("content-type"),
        "content_length": request.headers.get("content-length"),
        "body_size": len(body),
        "body_preview": body[:200].decode("utf-8", errors="replace"),
    }


@app.post("/debug-body")
async def debug_body(request: Request):
    body = await request.body()

    return {
        "content_type": request.headers.get("content-type"),
        "content_length": request.headers.get("content-length"),
        "body_size": len(body),
        "body_preview": body[:200].decode("utf-8", errors="replace"),
    }


@app.post("/recommendations")
def recomendar_dados(dados: DadosRecomendacao):
    resultados = recomendar(
        projetos=dados.projetos,
        preferencias=dados.preferencias,
        limite=dados.limite,
    )

    return {
        "quantidade": len(resultados),
        "recomendacoes": [
            resultado.model_dump()
            for resultado in resultados
        ],
    }