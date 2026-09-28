from app.rag.retriever import esg_retriever
from app.rag.knowledge_base import ESG_KNOWLEDGE_DOCUMENTS


def test_esg_knowledge_base_loaded():
    """Valida se a base de conhecimento ESG possui os documentos obrigatorios."""
    assert len(ESG_KNOWLEDGE_DOCUMENTS) >= 5
    categories = {doc["category"] for doc in ESG_KNOWLEDGE_DOCUMENTS}
    assert "MOBILIDADE_URBANA" in categories
    assert "ECONOMIA_CIRCULAR" in categories
    assert "GAMIFICACAO" in categories


def test_retriever_returns_metro_context():
    """Valida se a busca hibrida por metro recupera fatores de transporte publico."""
    query = "Quantos kg de CO2 economizo indo de metro?"
    context = esg_retriever.get_relevant_context(query, k=2)

    assert context != ""
    assert "Fonte:" in context
    assert ("metro" in context.lower() or "passageiro" in context.lower() or "co2" in context.lower())


def test_retriever_returns_recycling_context():
    """Valida se a busca hibrida por reciclagem recupera fatores do IPCC/Abrelpe."""
    query = "Quanto CO2 evita reciclar latinhas de aluminio?"
    context = esg_retriever.get_relevant_context(query, k=2)

    assert context != ""
    assert "Fonte:" in context
    assert ("aluminio" in context.lower() or "reciclagem" in context.lower() or "co2" in context.lower())
