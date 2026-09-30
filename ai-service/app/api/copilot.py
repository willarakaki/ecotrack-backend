import json
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.security.qwen_guardrail import qwen_guardrail
from app.security.pii_sanitizer import pii_sanitizer
from app.core.llm_factory import LLMFactory
from app.rag.retriever import esg_retriever

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
    rag_context_used: bool = Field(default=False, description="Indica se a resposta foi enriquecida com a base de conhecimento RAG")

COPILOT_BASE_PROMPT = """
Voce e o EcoTrack Copilot, o assistente virtual especialista em sustentabilidade corporativa,
reducao de emissoes de carbono de Escopo 3 e engajamento em praticas ESG.

Suas diretrizes:
1. Forneca dicas praticas, empaticas e fundamentadas nos dados tecnicos para o colaborador reduzir sua pegada.
2. Estimule o uso de transporte publico (metro, trem, onibus), caronas compartilhadas, bike e caminhada.
3. Incentive o descarte consciente e a reciclagem de materiais.
4. Explique com clareza as regras de EcoCoins e resgate de recompensas.
5. Sempre que citar estimativas de carbono ou pontuacao, baseie-se no CONHECIMENTO TECNICO fornecido abaixo.
6. Mantenha respostas concisas, claras e motivadoras.
"""

_copilot_llm = None

def get_copilot_llm():
    global _copilot_llm
    if _copilot_llm is None:
        _copilot_llm = LLMFactory.get_google_gemini(temperature=0.4)
    return _copilot_llm

def build_system_message_with_rag(query: str) -> SystemMessage:
    """Busca contexto semantico na base RAG e constroi o prompt do sistema enriquecido."""
    rag_context = esg_retriever.get_relevant_context(query, k=2)
    prompt_text = f"""{COPILOT_BASE_PROMPT}

CONHECIMENTO TECNICO RELEVANTE (RAG / Fatores Oficiais ESG):
{rag_context}
"""
    return SystemMessage(content=prompt_text)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_copilot(payload: ChatRequest):
    """
    Endpoint interativo sincronizado do EcoTrack AI Copilot com Guardrail Neural Qwen 2.5 (7B) + RAG.
    Pipeline: Qwen Guardrail (Jailbreak + Topical) -> PIISanitizer (Presidio) -> RAG Retrieval -> Gemini LLM.
    """
    user_input = payload.message.strip()
    if not user_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A mensagem nao pode ser vazia."
        )

    # 1. Pipeline de Seguranca: Guardrail Neural Qwen 2.5 (7B via Ollama / RTX 3070)
    verdict = qwen_guardrail.evaluate(user_input)
    if not verdict.is_safe:
        logger.warning(f"[Copilot API] Bloqueio de Seguranca por Qwen Guardrail: {verdict.reason}")
        return ChatResponse(
            reply="Sua mensagem foi bloqueada pelas diretrizes de seguranca e uso aceitavel.",
            blocked_by_guardrail=True,
            guardrail_reason=verdict.reason,
            sanitized_input=user_input,
            rag_context_used=False
        )

    # 2. Pipeline de Seguranca: Anonimizacao de PII (LGPD / Presidio)
    sanitized_input = pii_sanitizer.sanitize(user_input)

    # 3. Pipeline de Seguranca: Verificacao Topical (Escopo ESG)
    if not verdict.is_on_topic:
        logger.info(f"[Copilot API] Redirecionamento de topico por Qwen Guardrail: {verdict.reason}")
        redirect_msg = (
            "Como seu Copiloto de Sustentabilidade da EcoTrack, posso ajudar exclusivamente com "
            "dicas para reduzir sua pegada de carbono, mobilidade urbana, reciclagem e gestao de EcoCoins. "
            "Como podemos colaborar pelo meio ambiente hoje?"
        )
        return ChatResponse(
            reply=redirect_msg,
            blocked_by_guardrail=True,
            guardrail_reason="TOPICAL_DEVIATION",
            sanitized_input=sanitized_input,
            rag_context_used=False
        )

    # 4. Enriquecimento via RAG (Semantic Search) e Inferencia com a LLM
    try:
        system_msg = build_system_message_with_rag(sanitized_input)
        messages = [system_msg]
        
        for hist_msg in payload.history[-6:]:
            if hist_msg.role == "user":
                messages.append(HumanMessage(content=hist_msg.content))
            elif hist_msg.role == "assistant":
                messages.append(AIMessage(content=hist_msg.content))

        messages.append(HumanMessage(content=sanitized_input))
        llm = get_copilot_llm()
        response = llm.invoke(messages)
        
        return ChatResponse(
            reply=response.content if hasattr(response, "content") else str(response),
            blocked_by_guardrail=False,
            guardrail_reason=None,
            sanitized_input=sanitized_input,
            rag_context_used=True
        )

    except Exception as e:
        logger.error(f"[Copilot API] Erro ao invocar LLM: {e}")
        return ChatResponse(
            reply="Desculpe, nosso assistente sustentavel esta momentaneamente indisponivel. Tente novamente em instantes.",
            blocked_by_guardrail=False,
            guardrail_reason="INTERNAL_LLM_ERROR",
            sanitized_input=sanitized_input,
            rag_context_used=False
        )

@router.post("/chat/stream")
async def chat_stream_with_copilot(payload: ChatRequest):
    """
    Endpoint com suporte a Server-Sent Events (SSE) / Streaming em tempo real enriquecido com Qwen Guardrail + RAG.
    """
    user_input = payload.message.strip()
    if not user_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A mensagem nao pode ser vazia."
        )

    def event_generator():
        # 1. Pipeline de Seguranca: Guardrail Neural Qwen 2.5
        verdict = qwen_guardrail.evaluate(user_input)
        if not verdict.is_safe:
            err_payload = {
                "content": "Sua mensagem foi bloqueada pelas diretrizes de seguranca.",
                "blocked_by_guardrail": True,
                "reason": verdict.reason
            }
            yield f"data: {json.dumps(err_payload)}\n\n"
            yield "data: [DONE]\n\n"
            return

        # 2. Pipeline de Seguranca: PII Sanitizer
        sanitized_input = pii_sanitizer.sanitize(user_input)

        # 3. Pipeline de Seguranca: Topical Guard
        if not verdict.is_on_topic:
            redirect_payload = {
                "content": (
                    "Como seu Copiloto de Sustentabilidade da EcoTrack, posso ajudar exclusivamente com "
                    "dicas para reduzir sua pegada de carbono, mobilidade urbana, reciclagem e gestao de EcoCoins."
                ),
                "blocked_by_guardrail": True,
                "reason": "TOPICAL_DEVIATION"
            }
            yield f"data: {json.dumps(redirect_payload)}\n\n"
            yield "data: [DONE]\n\n"
            return

        # 4. RAG Retrieval e Inferencia com Streaming (Gemini)
        try:
            system_msg = build_system_message_with_rag(sanitized_input)
            messages = [system_msg]
            
            for hist_msg in payload.history[-6:]:
                if hist_msg.role == "user":
                    messages.append(HumanMessage(content=hist_msg.content))
                elif hist_msg.role == "assistant":
                    messages.append(AIMessage(content=hist_msg.content))
            messages.append(HumanMessage(content=sanitized_input))

            llm = get_copilot_llm()
            for chunk in llm.stream(messages):
                token_text = chunk.content if hasattr(chunk, "content") else str(chunk)
                if isinstance(token_text, list):
                    text = ""
                    for item in token_text:
                        if isinstance(item, dict) and "text" in item:
                            text += item["text"]
                        elif isinstance(item, str):
                            text += item
                    token_text = text
                elif not isinstance(token_text, str):
                    token_text = str(token_text)
                    
                if token_text:
                    yield f"data: {json.dumps({'content': token_text, 'blocked_by_guardrail': False, 'rag_context_used': True})}\n\n"
            
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"[Copilot API Stream] Erro durante streaming: {e}")
            yield f"data: {json.dumps({'content': 'Erro interno ao processar resposta do assistente.', 'error': True})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
