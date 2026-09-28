import logging
import re
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class PromptGuardResult(BaseModel):
    is_safe: bool = Field(description="True se o prompt for seguro para envio a LLM. False se for ataque.")
    attack_type: str | None = Field(default=None, description="Tipo de ataque detectado (ex: INJECTION, JAILBREAK, SYSTEM_LEAK).")
    risk_score: float = Field(default=0.0, description="Nivel de risco de 0.0 a 1.0.")
    reason: str = Field(default="", description="Justificativa do bloqueio.")

class PromptGuard:
    """
    Camada de Defesa contra Prompt Injection e Jailbreaks baseada no Llama Prompt Guard 2 / OWASP LLM01.
    Bloqueia tentativas de quebra de instrucoes ('Ignore previous instructions', 'DAN mode', etc).
    """

    # Assinaturas e vetores comuns de Jailbreak e Prompt Injection
    SUSPICIOUS_PATTERNS = [
        (r"ignore\s+(all\s+)?(previous|prior)\s+instructions?", "INJECTION", 0.95),
        (r"esque[cç]a\s+(todas\s+as\s+)?instru[cç][oõ]es\s+anteriores?", "INJECTION", 0.95),
        (r"you\s+are\s+now\s+(DAN|unfiltered|jailbroken)", "JAILBREAK", 0.98),
        (r"voce\s+agora\s+e\s+(um\s+modo\s+livre|sem\s+filtros|DAN)", "JAILBREAK", 0.98),
        (r"(reveal|print|show|display)\s+(the\s+)?(system\s+prompt|developer\s+mode)", "SYSTEM_LEAK", 0.90),
        (r"(revele|mostre|imprima)\s+(o\s+)?prompt\s+do\s+sistema", "SYSTEM_LEAK", 0.90),
        (r"base64\s*:\s*[A-Za-z0-9+/=]{20,}", "OBFUSCATED_PAYLOAD", 0.85),
        (r"act\s+as\s+an\s+unrestricted", "JAILBREAK", 0.92),
    ]

    def validate(self, user_prompt: str) -> PromptGuardResult:
        """
        Analisa o prompt do usuario e bloqueia tentativas hostis antes de chegar a LLM.
        """
        if not user_prompt or not user_prompt.strip():
            return PromptGuardResult(is_safe=True, risk_score=0.0)

        clean_text = user_prompt.lower()

        for pattern, attack_type, score in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, clean_text, re.IGNORECASE):
                logger.warning(f"[PromptGuard] Ataque detectado! Tipo: {attack_type} | Padrao: {pattern}")
                return PromptGuardResult(
                    is_safe=False,
                    attack_type=attack_type,
                    risk_score=score,
                    reason=f"Prompt bloqueado pelas politicas de seguranca (Padrao: {attack_type})."
                )

        # Prompt limpo
        return PromptGuardResult(is_safe=True, risk_score=0.0)

prompt_guard = PromptGuard()
