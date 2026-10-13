from app.models import Projeto, PreferenciaTopico
from app.recommender import recomendar


def test_recomenda_projeto_relacionado_ao_topico():
    projetos = [
        Projeto(
            numero="001",
            titulo="Inteligência artificial aplicada à educação",
            resumo="Uso de machine learning em sistemas educacionais",
            topicos=["machine learning", "educação"],
        ),
        Projeto(
            numero="002",
            titulo="Estudo de biodiversidade",
            resumo="Análise de espécies vegetais",
            topicos=["biologia", "meio ambiente"],
        ),
    ]

    preferencias = [
        PreferenciaTopico(topico="machine learning", peso=1.0)
    ]

    resultados = recomendar(projetos, preferencias)

    assert len(resultados) == 2
    assert resultados[0].projeto.numero == "001"
    assert resultados[0].pontuacao > resultados[1].pontuacao


def test_sem_preferencias_nao_recomenda():
    projetos = [
        Projeto(numero="001", titulo="Projeto de teste")
    ]

    resultados = recomendar(projetos, [])

    assert resultados == []