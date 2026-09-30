import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class TopicalGuardResult(BaseModel):
    is_on_topic: bool = Field(description="True se a pergunta for relevante ao contexto ESG/Sustentabilidade.")
    confidence: float = Field(default=1.0, description="Nivel de confianca da classificacao.")
    redirect_message: str | None = Field(default=None, description="Mensagem de redirecionamento caso esteja fora de topico.")

class TopicalGuard:
    """
    Topical Guardrail para o EcoTrack Copilot.
    Garante que o chatbot atenda estritamente ao proposito do negocio:
    - Sustentabilidade corporativa e pessoal
    - Rastreamento e reducao de pegada de carbono (Escopo 3)
    - Mobilidade sustentavel (transporte publico, bike, carona)
    - Descarte e reciclagem de residuos
    - EcoCoins e engajamento em gamificacao ESG
    """

    ALLOWED_KEYWORDS = {
        "carbono", "co2", "sustentabilidade", "esg", "emissao", "emissoes", "escopo 3",
        "reciclagem", "reciclar", "lixo", "residuo", "residuos", "plastico", "organico",
        "transporte", "metro", "onibus", "trem", "bicicleta", "bike", "carona", "uber",
        "ecocoin", "ecocoins", "pontos", "recompensa", "gamificacao", "desafio",
        "energia", "agua", "arvore", "clima", "pegada", "verde", "voucher",
        "sim", "nao", "não", "claro", "ola", "olá", "oi", "quero", "queria",
        "bom", "boa", "dia", "tarde", "noite", "ajuda", "dicas", "dica", "ok", "valeu"
    }

    OUT_OF_TOPIC_REDIRECT = (
        "Como seu Copiloto de Sustentabilidade da EcoTrack, posso ajudar exclusivamente com "
        "dicas para reduzir sua pegada de carbono, mobilidade urbana, reciclagem e gestao de EcoCoins. "
        "Como podemos colaborar pelo meio ambiente hoje?"
    )

    def check_topic(self, user_message: str) -> TopicalGuardResult:
        """
        Verifica se a mensagem do usuario possui relacao com os pilares ESG do EcoTrack.
        """
        if not user_message or not user_message.strip():
            return TopicalGuardResult(is_on_topic=True)

        tokens = set(user_message.lower().split())
        
        # Interseccao de palavras-chave
        matched = tokens.intersection(self.ALLOWED_KEYWORDS)
        
        # Se contiver pelo menos uma palavra-chave ou termo derivado
        if matched or any(kw in user_message.lower() for kw in self.ALLOWED_KEYWORDS):
            return TopicalGuardResult(is_on_topic=True, confidence=0.95)

        logger.info(f"[TopicalGuard] Pergunta fora do escopo ESG detectada: '{user_message[:50]}...'")
        return TopicalGuardResult(
            is_on_topic=False,
            confidence=0.85,
            redirect_message=self.OUT_OF_TOPIC_REDIRECT
        )

topical_guard = TopicalGuard()
