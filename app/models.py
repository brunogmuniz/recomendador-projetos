from pydantic import BaseModel, Field


class Projeto(BaseModel):
    numero: str
    titulo: str
    dataInicio: str | None = None
    dataFim: str | None = None
    situacao: str | None = None
    resumo: str | None = None
    classificacaoCNPQ: str | None = None
    linhaPesquisa: str | None = None
    responsavel: str | None = None
    tipoOrientacao: str | None = None
    topicos: list[str] = Field(default_factory=list)


class PreferenciaTopico(BaseModel):
    topico: str
    peso: float


class Recomendacao(BaseModel):
    projeto: Projeto
    pontuacao: float