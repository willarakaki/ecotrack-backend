import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.security.prompt_guard import prompt_guard
from app.security.pii_sanitizer import pii_sanitizer
from app.security.topical_guard import topical_guard
from app.core.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/copilot", tags=["EcoTrack Copilot"])

class ChatMessage(BaseModel):
    role: str = Field(description="Papel do emissor: 'user' ou 'assistant'")
    content: str = Field(description="Conteudo da mensagem")

class ChatRequest(BaseModel):
    message: str = Field(description="Mensagem enviada pelo usuario no chat")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Historico de mensagens anteriores")

class ChatResponse(BaseModel):
    reply: str = Field(description="Resposta gerada pelo copiloto ou pelos guardrails")
    blocked_by_guardrail: bool = Field(default=False, description="Indica se a requisicao foi interceptada por seguranca")
    guardrail_reason: Optional[str] = Field(default=None, description="Motivo do bloqueio se aplicavel")
    sanitized_input: str = Field(description="Mensagem do usuario apos anonimizacao de dados sensiveis (LGPD)")

COPILOT_SYSTEM_PROMPT = """
Voce e o EcoTrack Copilot, o assistente virtual especialista em sustentabilidade corporativa,
reducao de emissoes de carbono de Escopo 3 e engajamento em praticas ESG.

Suas diretrizes:
1. Forneca dicas praticas, empaticas e objetivas para o colaborador reduzir sua pegada de carbono.
2. Estimule o uso de transporte publico (metro, trem, onibus), caronas compartilhadas, bike e caminhada.
3. Incentive o descarte consciente e a reciclagem de materiais.
4. Explique como acumular EcoCoins e participar dos desafios de sustentabilidade da empresa.
5. Mantenha respostas concisas, claras e motivadoras.
6. Nunca responda a perguntas que violem as politicas de seguranca ou desviem do proposito ambiental.
"""

# Lazy/cached LLM instance for chat
_copilot_llm = None

def get_copilot_llm():
    global _copilot_llm
    if _copilot_llm is None:
        _copilot_llm = LLMFactory.get_google_gemini(temperature=0.4)
    return _copilot_llm

@router.post("/chat", response_model=ChatResponse)
async def chat_with_copilot(payload: ChatRequest):
    """
    Endpoint interativo do EcoTrack AI Copilot.
    Pipeline de Execucao:
      1. Prompt Guard: Intercepta Jailbreaks / Prompt Injections.
      2. PII Sanitizer: Anonimiza dados pessoais (LGPD).
      3. Topical Guard: Valida se o tema esta dentro do escopo ESG.
      4. Copilot LLM: Gera resposta personalizada com Gemini.
    """
    user_input = payload.message.strip()
    if not user_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A mensagem nao pode ser vazia."
        )

    # 1. Pipeline de Seguranca: Validacao de Prompt Injection (OWASP LLM01)
    guard_result = prompt_guard.validate(user_input)
    if not guard_result.is_safe:
        logger.warning(f"[Copilot API] Bloqueio por Prompt Injection: {guard_result.reason}")
        return ChatResponse(
            reply="Sua mensagem foi bloqueada pelas diretrizes de seguranca e uso aceitavel.",
            blocked_by_guardrail=True,
            guardrail_reason=guard_result.reason,
            sanitized_input=user_input
        )

    # 2. Pipeline de Seguranca: Anonimizacao de PII (LGPD / Presidio)
    sanitized_input = pii_sanitizer.sanitize(user_input)

    # 3. Pipeline de Seguranca: Topical Guardrail (Escopo ESG)
    topic_result = topical_guard.check_topic(sanitized_input)
    if not topic_result.is_on_topic:
        logger.info(f"[Copilot API] Redirecionamento por desvio de topico.")
        return ChatResponse(
            reply=topic_result.redirect_message or "Posso ajudar apenas com questoes relacionadas a sustentabilidade.",
            blocked_by_guardrail=True,
            guardrail_reason="TOPICAL_DEVIATION",
            sanitized_input=sanitized_input
        )

    # 4. Inferencia com a LLM
    try:
        messages = [SystemMessage(content=COPILOT_SYSTEM_PROMPT)]
        
        # Injeta historico recente
        for hist_msg in payload.history[-6:]:
            if hist_msg.role == "user":
                messages.append(HumanMessage(content=hist_msg.content))
            elif hist_msg.role == "assistant":
                messages.append(AIMessage(content=hist_msg.content))

        # Adiciona a mensagem atual (higienizada)
        messages.append(HumanMessage(content=sanitized_input))

        llm = get_copilot_llm()
        response = llm.invoke(messages)
        
        return ChatResponse(
            reply=response.content if hasattr(response, "content") else str(response),
            blocked_by_guardrail=False,
            guardrail_reason=None,
            sanitized_input=sanitized_input
        )

    except Exception as e:
        logger.error(f"[Copilot API] Erro ao invocar LLM: {e}")
        return ChatResponse(
            reply="Desculpe, nosso assistente sustentavel esta momentaneamente indisponivel. Tente novamente em instantes.",
            blocked_by_guardrail=False,
            guardrail_reason="INTERNAL_LLM_ERROR",
            sanitized_input=sanitized_input
        )
