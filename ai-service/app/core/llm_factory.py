import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Factory pattern para instanciar Modelos de Linguagem (LLMs).
    Garante o Princípio Open-Closed (SOLID): Se adicionarmos Groq ou OpenAI amanhã,
    só criamos um novo método aqui, sem quebrar os Agentes do LangGraph.
    """
    
    @staticmethod
    def get_google_gemini(model_name: str = "gemini-3.5-flash", temperature: float = 0.1) -> ChatGoogleGenerativeAI:
        """Instancia o Gemini (usado para inferência pesada / OCR)."""
        if not settings.google_api_key:
            logger.warning("GOOGLE_API_KEY não configurada no .env!")
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=settings.google_api_key,
            temperature=temperature
        )

    @staticmethod
    def get_local_ollama(model_name: str = "llama3", temperature: float = 0.1) -> ChatOllama:
        """Instancia modelo rodando local via Ollama (usado como Gatekeeper rápido e gratuito)."""
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=model_name,
            temperature=temperature
        )

    @staticmethod
    def get_default_validator() -> ChatGoogleGenerativeAI:
        """Retorna o modelo primário para validação corporativa."""
        return LLMFactory.get_google_gemini()
