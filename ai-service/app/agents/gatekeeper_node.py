import logging
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from app.orchestrator.state import EvidenceValidationState
from app.core.llm_factory import LLMFactory

logger = logging.getLogger(__name__)


class GatekeeperOutput(BaseModel):
    is_valid_format: bool = Field(
        description="True se a imagem for minimamente legivel. False se for obvio lixo/foto preta."
    )
    reason: str = Field(description="O motivo da recusa, se for invalido.")


# Usa um modelo local (ex: llava para visao ou llama3 para triagem de texto) para reduzir custos
slm_gatekeeper = LLMFactory.get_local_ollama(model_name="llava", temperature=0.0)
structured_gatekeeper = slm_gatekeeper.with_structured_output(GatekeeperOutput)


def gatekeeper_node(state: EvidenceValidationState) -> dict:
    """
    No Gatekeeper (Ollama Local).
    Triagem rapida: Se a evidencia for um obvio lixo (ex: foto toda preta),
    barramos aqui. Isso economiza chamadas de API (Gemini).
    """
    logger.info(f"[Gatekeeper Node] Triagem inicial da acao {state['action_id']}...")

    prompt_text = f"""
    Voce e um classificador inicial de qualidade.
    Nao julgue se a acao ESG e valida, APENAS julgue se a evidencia abaixo e LIXO (ex: foto preta, arquivo corrompido).

    Acao esperada: {state['action_type']}
    Evidencia fornecida: {state['evidence_url']}
    """

    try:
        result: GatekeeperOutput = structured_gatekeeper.invoke([HumanMessage(content=prompt_text)])

        if not result.is_valid_format:
            logger.warning(f"[Gatekeeper Node] Lixo detectado! Bloqueando acao {state['action_id']}.")
            return {
                "verdict": "REJECTED",
                "reasoning": f"Triagem Inicial falhou: {result.reason}",
                "co2_saved": 0.0
            }

        logger.info("[Gatekeeper Node] Triagem passou. Encaminhando para auditoria profunda.")
        return {}

    except Exception as e:
        logger.error(f"[Gatekeeper Node] Erro na SLM local, permitindo bypass para a nuvem: {e}")
        return {}
