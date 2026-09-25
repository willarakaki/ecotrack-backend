import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from app.core.config import settings
from app.orchestrator.state import EvidenceValidationState

logger = logging.getLogger(__name__)

# 1. Output Rigoroso: Forçamos o Gemini a responder em JSON tipado!
class ValidationOutput(BaseModel):
    verdict: str = Field(description="Deve ser EXATAMENTE um destes: 'APPROVED', 'REJECTED' ou 'FRAUD'")
    reasoning: str = Field(description="Explicação sucinta de como você chegou a esse veredito e ao cálculo de CO2.")
    co2_saved: float = Field(description="Estimativa de kg de CO2 poupado. Deve ser 0.0 se for FRAUD ou REJECTED.")

# 2. Inicialização do Modelo (Usamos o Flash por ser hiper-rápido para validações em massa)
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    api_key=settings.GEMINI_API_KEY,
    temperature=0.1 # Temperatura baixa para respostas mais determinísticas/matemáticas
)

# Acoplamos a saída estruturada Pydantic à LLM
structured_llm = llm.with_structured_output(ValidationOutput)

def validate_evidence_node(state: EvidenceValidationState) -> dict:
    """
    Nó principal do LangGraph.
    Recebe o estado com a URL da foto, consulta o Gemini, e devolve as chaves atualizadas.
    """
    logger.info(f"[LLM Node] Analisando ação {state['action_id']} do tipo {state['action_type']}...")

    # Padrão de Segurança (OWASP/Privacy): 
    # Repare que NÃO injetamos o userId no prompt. A IA não precisa saber QUEM fez a ação.
    prompt_text = f"""
    Você é um Engenheiro Ambiental e Auditor de Fraudes Especialista em ESG.
    Avalie a seguinte evidência de uma ação sustentável:
    
    Tipo de Ação: {state['action_type']}
    Descrição/Conteúdo da Evidência: {state['evidence_url']}
    
    Regras de Negócio:
    1. Se parecer uma tentativa clara de enganar o sistema (ex: foto de tela, internet), veredito = FRAUD.
    2. Se não cumprir os requisitos da ação, veredito = REJECTED.
    3. Se for legítima, veredito = APPROVED, e faça uma estimativa razoável de Kg de CO2 economizado.
    """
    
    try:
        # Invoca a LLM
        result: ValidationOutput = structured_llm.invoke([HumanMessage(content=prompt_text)])
        
        logger.info(f"[LLM Node] Veredito gerado: {result.verdict}")
        
        # O retorno é mesclado automaticamente no "EvidenceValidationState" pelo LangGraph
        return {
            "verdict": result.verdict,
            "reasoning": result.reasoning,
            "co2_saved": result.co2_saved
        }
        
    except Exception as e:
        logger.error(f"[LLM Node] Erro crítico de inferência: {e}")
        # Circuito de Falha / Fallback defensivo
        return {
            "verdict": "REJECTED",
            "reasoning": "A análise automatizada falhou. Ação rejeitada preventivamente.",
            "co2_saved": 0.0
        }
