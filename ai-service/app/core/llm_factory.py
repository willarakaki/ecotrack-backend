import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Factory pattern para instanciar Modelos de Linguagem (LLMs) e Embeddings.
    Garante o Principio Open-Closed (SOLID): Se adicionarmos Groq ou OpenAI amanha,
    so criamos um novo metodo aqui, sem quebrar os Agentes do LangGraph ou o RAG.
    """
    
    @staticmethod
    def get_google_gemini(model_name: str = "gemini-3.5-flash", temperature: float = 0.1) -> ChatGoogleGenerativeAI:
        """Instancia o Gemini (usado para inferencia pesada / OCR / Copilot)."""
        api_key = settings.google_api_key
        if not api_key:
            logger.warning("GOOGLE_API_KEY nao configurada no .env! Usando dummy para evitar crash no boot.")
            api_key = "dummy-key-for-boot"
            
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature
        )

    @staticmethod
    def get_local_ollama(model_name: str = "llama3", temperature: float = 0.1) -> ChatOllama:
        """Instancia modelo rodando local via Ollama (usado como Gatekeeper rapido e gratuito)."""
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=model_name,
            temperature=temperature
        )

    @staticmethod
    def get_qwen_guardrail(model_name: str = "qwen2.5:7b", temperature: float = 0.0) -> ChatOllama:
        """
        Instancia o Qwen 2.5 (7B) rodando na GPU local (RTX 3070) via Ollama.
        Especializado em atuacao como Guardrail Neural (Topical + Jailbreak Filter).
        """
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=model_name,
            temperature=temperature
        )

    @staticmethod
    def get_default_validator() -> ChatGoogleGenerativeAI:
        """Retorna o modelo primario para validacao corporativa."""
        return LLMFactory.get_google_gemini()

    @staticmethod
    def get_embeddings():
        """Instancia o modelo de Embeddings para busca vetorial RAG."""
        api_key = settings.google_api_key
        if not api_key or api_key == "dummy-key-for-ci" or api_key == "dummy-key-for-boot":
            from langchain_core.embeddings import FakeEmbeddings
            return FakeEmbeddings(size=768)
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )
        except Exception as e:
            logger.warning(f"[LLMFactory] Falha ao instanciar embeddings do Google: {e}. Usando FakeEmbeddings.")
            from langchain_core.embeddings import FakeEmbeddings
            return FakeEmbeddings(size=768)
