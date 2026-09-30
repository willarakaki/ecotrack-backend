import re
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

        # Remove pontuacao para match exato
        clean_msg = re.sub(r'[^a-zA-Z0-9\s]', '', user_message.lower())
        tokens = set(clean_msg.split())
        
        matched = tokens.intersection(self.ALLOWED_KEYWORDS)
        
        # Greetings/Curto: apenas se a mensagem for *muito* curta (ex: "sim", "ok", "ola", "bom dia")
        is_short_greeting = len(tokens) <= 3 and matched
        
        # Palavras core (com mais de 3 letras e que nao sao greetings) garantem aprovacao
        core_keywords = {kw for kw in self.ALLOWED_KEYWORDS if kw not in {"sim", "nao", "nǜo", "claro", "ola", "olǭ", "oi", "bom", "boa", "dia", "tarde", "noite", "ok"}}
        has_core_topic = tokens.intersection(core_keywords)
        
        if has_core_topic or is_short_greeting:
            return TopicalGuardResult(is_on_topic=True, confidence=0.95)

        logger.info(f"[TopicalGuard] Pergunta fora do escopo ESG detectada: '{user_message[:50]}...'")
        return TopicalGuardResult(
            is_on_topic=False,
            confidence=0.85,
            redirect_message=self.OUT_OF_TOPIC_REDIRECT
        )

topical_guard = TopicalGuard()
