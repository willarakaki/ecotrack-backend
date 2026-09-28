import logging
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from app.core.llm_factory import LLMFactory
from app.rag.knowledge_base import ESG_KNOWLEDGE_DOCUMENTS

logger = logging.getLogger(__name__)


class ESGRetriever:
    """
    Motor RAG para busca semantica de normas ESG, GHG Protocol e regras EcoTrack.
    Utiliza busca hibrida (Keyword Matching + Dense Vector Similarity)
    para garantir recuperacao confiavel tanto em producao quanto em ambientes de CI.
    """

    def __init__(self):
        self._vector_store = None
        self._documents = []
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Indexa os documentos da base de conhecimento com embeddings vetoriais."""
        try:
            embeddings = LLMFactory.get_embeddings()

            self._documents = [
                Document(
                    page_content=doc["content"],
                    metadata={
                        "id": doc["id"],
                        "category": doc["category"],
                        "title": doc["title"]
                    }
                )
                for doc in ESG_KNOWLEDGE_DOCUMENTS
            ]

            self._vector_store = InMemoryVectorStore.from_documents(
                documents=self._documents,
                embedding=embeddings
            )
            logger.info(f"[ESGRetriever] Base vetorial RAG inicializada com {len(self._documents)} documentos.")

        except Exception as e:
            logger.error(f"[ESGRetriever] Erro ao indexar documentos RAG: {e}")
            self._vector_store = None

    def _keyword_boost(self, query: str) -> list[Document]:
        """Calcula relevancia por correspondencia de termos-chave para garantir busca hibrida."""
        query_words = set(query.lower().split())
        scored_docs = []

        for doc in self._documents:
            score = 0
            text_lower = (doc.metadata.get("title", "") + " " + doc.page_content).lower()
            for word in query_words:
                if len(word) > 3 and word in text_lower:
                    score += 2 if word in doc.metadata.get("title", "").lower() else 1

            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs]

    def get_relevant_context(self, query: str, k: int = 2) -> str:
        """
        Executa busca hibrida (termos exatos + similaridade vetorial)
        e retorna o contexto formatado para o Copilot.
        """
        if not query or not query.strip():
            return "Consulte as diretrizes do GHG Protocol e as regras oficiais de EcoCoins da EcoTrack."

        results = []

        # 1. Recupera candidatos por casamento de termos-chave (Sparse)
        keyword_matches = self._keyword_boost(query)
        for doc in keyword_matches[:k]:
            if doc not in results:
                results.append(doc)

        # 2. Complementa com busca vetorial se necessario (Dense)
        if len(results) < k and self._vector_store:
            try:
                vector_matches = self._vector_store.similarity_search(query, k=k)
                for doc in vector_matches:
                    if doc not in results and len(results) < k:
                        results.append(doc)
            except Exception as e:
                logger.error(f"[ESGRetriever] Erro durante busca vetorial: {e}")

        # Se nenhum resultado for encontrado, retorna os primeiros documentos da base
        if not results:
            results = self._documents[:k]

        context_parts = []
        for i, doc in enumerate(results, 1):
            title = doc.metadata.get("title", f"Documento {i}")
            context_parts.append(f"--- Fonte: {title} ---\n{doc.page_content}")

        return "\n\n".join(context_parts)


# Instancia singleton para uso compartilhado
esg_retriever = ESGRetriever()
