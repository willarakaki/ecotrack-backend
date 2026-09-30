import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Factory pattern para instanciar Modelos de Linguagem (LLMs) e Embeddings.
    """
    
    @staticmethod
    def get_google_gemini(model_name: str = "gemini-3.5-flash", temperature: float = 0.1):
        """Instancia o Gemini com Fallback Model e Max Retries."""
        api_key = settings.google_api_key
        if not api_key:
            logger.warning("GOOGLE_API_KEY nao configurada! Usando dummy para boot.")
            api_key = "dummy-key-for-boot"
            
        # Modelo principal (Pro)
        primary_llm = ChatGoogleGenerativeAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            max_retries=2 # Tenta 2 vezes caso a API de timeout
        )

        # Modelo fallback mais rapido/barato (Flash) caso o Pro falhe continuamente
        fallback_llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            api_key=api_key,
            temperature=temperature,
            max_retries=1
        )
        
        # Implementacao do padrao Fallback (Resiliencia e Custo)
        return primary_llm.with_fallbacks([fallback_llm])

    @staticmethod
    def get_local_ollama(model_name: str = "llama3", temperature: float = 0.1) -> ChatOllama:
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=model_name,
            temperature=temperature
        )

    @staticmethod
    def get_qwen_guardrail(model_name: str = "qwen2.5:7b", temperature: float = 0.0) -> ChatOllama:
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=model_name,
            temperature=temperature
        )

    @staticmethod
    def get_default_validator():
        return LLMFactory.get_google_gemini()

    @staticmethod
    def get_embeddings():
        api_key = settings.google_api_key
        if not api_key or api_key == "dummy-key-for-boot":
            from langchain_core.embeddings import FakeEmbeddings
            return FakeEmbeddings(size=768)
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )
        except Exception:
            from langchain_core.embeddings import FakeEmbeddings
            return FakeEmbeddings(size=768)
