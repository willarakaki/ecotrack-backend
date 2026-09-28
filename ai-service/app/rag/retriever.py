import logging
from typing import List
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from app.core.llm_factory import LLMFactory
from app.rag.knowledge_base import ESG_KNOWLEDGE_DOCUMENTS

logger = logging.getLogger(__name__)

class ESGRetriever:
    """
    Motor RAG para busca semantica de normas ESG, GHG Protocol e regras EcoTrack.
    Utiliza InMemoryVectorStore para consultas vetoriais de altissima velocidade.
    """

    def __init__(self):
        self._vector_store = None
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Indexa os documentos da base de conhecimento com embeddings vetoriais."""
        try:
            embeddings = LLMFactory.get_embeddings()
            
            # Converte dicionarios em Documentos LangChain
            documents = [
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
                documents=documents,
                embedding=embeddings
            )
            logger.info(f"[ESGRetriever] Base vetorial RAG inicializada com {len(documents)} documentos.")

        except Exception as e:
            logger.error(f"[ESGRetriever] Erro ao indexar documentos RAG: {e}")
            self._vector_store = None

    def get_relevant_context(self, query: str, k: int = 2) -> str:
        """
        Executa busca semantica pelo query do usuario e retorna o contexto formatado.
        """
        if not self._vector_store or not query or not query.strip():
            # Fallback direto com texto resumido se vector store nao estiver pronto
            return "Consulte as diretrizes do GHG Protocol e as regras oficiais de EcoCoins da EcoTrack."

        try:
            results = self._vector_store.similarity_search(query, k=k)
            if not results:
                return ""

            context_parts = []
            for i, doc in enumerate(results, 1):
                title = doc.metadata.get("title", f"Documento {i}")
                context_parts.append(f"--- Fonte: {title} ---\n{doc.page_content}")

            return "\n\n".join(context_parts)

        except Exception as e:
            logger.error(f"[ESGRetriever] Erro durante busca semantica: {e}")
            return ""

# Instancia singleton para uso compartilhado
esg_retriever = ESGRetriever()
