import logging
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from app.orchestrator.state import EvidenceValidationState
from app.core.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

# 1. Output Rigoroso: Forcamos o Gemini a responder em JSON tipado!
class ValidationOutput(BaseModel):
    verdict: str = Field(description="Deve ser EXATAMENTE um destes: 'APPROVED', 'REJECTED' ou 'FRAUD'")
    reasoning: str = Field(description="Explicacao sucinta de como voce chegou a esse veredito e ao calculo de CO2.")
    co2_saved: float = Field(description="Estimativa de kg de CO2 poupado. Deve ser 0.0 se for FRAUD ou REJECTED.")

# 2. Inicializacao do Modelo via Factory
llm = LLMFactory.get_google_gemini()

# Acoplamos a saida estruturada Pydantic a LLM
structured_llm = llm.with_structured_output(ValidationOutput)

def validate_evidence_node(state: EvidenceValidationState) -> dict:
    """
    No principal do LangGraph.
    Recebe o estado com a URL da foto, consulta o Gemini, e devolve as chaves atualizadas.
    """
    logger.info(f"[LLM Node] Analisando acao {state['action_id']} do tipo {state['action_type']}...")

    # Padrao de Seguranca (OWASP/Privacy): 
    # Repare que NAO injetamos o userId no prompt. A IA nao precisa saber QUEM fez a acao.
    prompt_text = f"""
    Voce e um Engenheiro Ambiental e Auditor de Fraudes Especialista em ESG.
    Avalie a seguinte evidencia de uma acao sustentavel:
    
    Tipo de Acao: {state['action_type']}
    Descricao/Conteudo da Evidencia: {state['evidence_url']}
    
    Regras de Negocio:
    1. Se parecer uma tentativa clara de enganar o sistema (ex: foto de tela, internet), veredito = FRAUD.
    2. Se nao cumprir os requisitos da acao, veredito = REJECTED.
    3. Se for legitima, veredito = APPROVED, e faca uma estimativa razoavel de Kg de CO2 economizado.
    """
    
    try:
        # Invoca a LLM
        result: ValidationOutput = structured_llm.invoke([HumanMessage(content=prompt_text)])
        
        logger.info(f"[LLM Node] Veredito gerado: {result.verdict}")
        
        # O retorno e mesclado automaticamente no "EvidenceValidationState" pelo LangGraph
        return {
            "verdict": result.verdict,
            "reasoning": result.reasoning,
            "co2_saved": result.co2_saved
        }
        
    except Exception as e:
        logger.error(f"[LLM Node] Erro critico de inferencia: {e}")
        # Circuito de Falha / Fallback defensivo
        return {
            "verdict": "REJECTED",
            "reasoning": "A analise automatizada falhou. Acao rejeitada preventivamente.",
            "co2_saved": 0.0
        }
