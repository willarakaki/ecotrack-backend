import logging
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from app.agents.state import EvidenceValidationState
from app.core.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

class GatekeeperOutput(BaseModel):
    is_valid_format: bool = Field(description="True se a imagem/texto for minimamente legível e coerente com o tipo de ação. False se for óbvio lixo, foto preta, borrada, ou sem contexto.")
    reason: str = Field(description="O motivo da recusa, se for inválido.")

# Usa um modelo local (ex: llava para visão ou llama3 para triagem de texto) para reduzir custos
# O Factory encapsula a lógica de instanciar o Ollama
slm_gatekeeper = LLMFactory.get_local_ollama(model_name="llava", temperature=0.0)
structured_gatekeeper = slm_gatekeeper.with_structured_output(GatekeeperOutput)

def gatekeeper_node(state: EvidenceValidationState) -> dict:
    """
    Nó Gatekeeper (Ollama Local).
    Triagem rápida: Se a evidência for um óbvio lixo (ex: foto toda preta),
    barramos aqui. Isso economiza chamadas de API (Gemini).
    """
    logger.info(f"[Gatekeeper Node] Triagem inicial da ação {state['action_id']}...")

    prompt_text = f"""
    Você é um classificador inicial de qualidade.
    Não julgue se a ação ESG é válida, APENAS julgue se a evidência abaixo é LIXO (ex: foto preta, texto sem nexo, arquivo corrompido).
    
    Ação esperada: {state['action_type']}
    Evidência fornecida: {state['evidence_url']}
    """
    
    try:
        result: GatekeeperOutput = structured_gatekeeper.invoke([HumanMessage(content=prompt_text)])
        
        if not result.is_valid_format:
            logger.warning(f"[Gatekeeper Node] Lixo detectado! Bloqueando ação {state['action_id']}.")
            # Se for lixo, já cravamos o veredito como REJECTED e impedimos de ir pro Gemini
            return {
                "verdict": "REJECTED",
                "reasoning": f"Triagem Inicial falhou: {result.reason}",
                "co2_saved": 0.0
            }
        
        logger.info(f"[Gatekeeper Node] Triagem passou. Encaminhando para auditoria profunda.")
        # Se passar, retornamos dicionário vazio ou apenas o necessário, o LangGraph mantém o estado
        return {}
        
    except Exception as e:
        logger.error(f"[Gatekeeper Node] Erro na SLM local, permitindo bypass para a nuvem: {e}")
        # Fallback: Se o Ollama cair, passamos adiante pro Gemini resolver (Fail-Open)
        return {}
