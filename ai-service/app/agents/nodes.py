import logging
from typing import Optional
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from app.orchestrator.state import EvidenceValidationState
from app.core.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

# 1. Output Rigoroso do VLM: Forcamos o Gemini a responder em JSON tipado!
class ValidationOutput(BaseModel):
    verdict: str = Field(description="Deve ser EXATAMENTE um destes: 'APPROVED', 'REJECTED' ou 'FRAUD'")
    reasoning: str = Field(description="Explicacao sucinta da analise visual/OCR e justificativa do calculo de CO2.")
    co2_saved: float = Field(default=0.0, description="Estimativa de kg de CO2 poupado. Deve ser 0.0 se for FRAUD ou REJECTED.")
    detected_modality: Optional[str] = Field(default=None, description="Modal detectado no OCR: 'METRO', 'TREM', 'ONIBUS', 'UBER_POOL', 'BIKE', 'RECICLAGEM', 'DESCONHECIDO'")
    estimated_distance_km: Optional[float] = Field(default=None, description="Distancia estimada da viagem em km se extraida de ticket/print.")

# 2. Inicializacao do Modelo VLM via Factory
llm = LLMFactory.get_google_gemini()

# Acoplamos a saida estruturada Pydantic a LLM
structured_llm = llm.with_structured_output(ValidationOutput)

def validate_evidence_node(state: EvidenceValidationState) -> dict:
    """
    No principal do LangGraph: VLM Evidence Auditor.
    Especialista em OCR e visao computacional de tickets de metro/trem,
    prints de corridas Uber/99 e comprovantes de acoes sustentaveis.
    """
    logger.info(f"[VLM Node] Auditando evidencia da acao {state['action_id']} do tipo {state['action_type']}...")

    # Prompt especializado em VLM (Vision-Language) para comprovantes de mobilidade e sustentabilidade
    prompt_text = f"""
    Voce e um Auditor Especialista em OCR e Fraudes ESG para Rastreamento de Emissoes de Escopo 3.
    Sua missao e inspecionar visualmente o comprovante/evidencia anexado:

    Tipo de Acao Declarada: {state['action_type']}
    URL/Comprovante: {state['evidence_url']}

    DIRETRIZES DE AUDITORIA VISUAL (OCR):
    1. TICKETS DE TRANSPORTE PUBLICO (Metro, Trem, Onibus):
       - Verifique se ha elementos tipicos de bilhete (logotipo da concessionaria, data, horario, estacao ou validacao).
       - Deslocamento de transporte de massa evita aproximadamente 0.12 kg de CO2 por km em relacao a carro particular a combustao.
       - Se for ticket valido sem km explicitado, estime viagem urbana padrao (12 km = ~1.44 kg CO2).
    
    2. PRINTS DE APLICATIVOS DE MOBILIDADE (Uber, 99, Caronas):
       - Identifique se e categoria sustentavel ou carona compartilhada (ex: Uber Juntos, Uber Green, ou trajeto com múltiplos passageiros).
       - Extraia a distancia em km percorrida se visivel no print.
    
    3. FOTOS DE RECICLAGEM E RESIDUOS:
       - Valide se a foto mostra lixeiras de coleta seletiva ou separacao legitima de materiais (plastico, metal, papel, vidro).
       - 1 kg de material reciclado evita em media 1.5 kg CO2.
    
    4. REGRAS ANTIFRAUDE RIGOROSAS:
       - Se for print de tela reutilizado, imagem baixada da internet de bancos de imagem, foto preta ou duplicada: marque 'FRAUD'.
       - Se o comprovante for ilegivel, cortado ou de outra data nao condizente: marque 'REJECTED'.
       - Se for legitimo: marque 'APPROVED' e calcule o CO2 poupado.
    """

    # Construcao de mensagem multimodal compativel com o Gemini VLM
    evidence_url = state.get("evidence_url", "")
    if evidence_url.startswith("http://") or evidence_url.startswith("https://") or evidence_url.startswith("data:image"):
        message_content = [
            {"type": "text", "text": prompt_text},
            {"type": "image_url", "image_url": evidence_url}
        ]
    else:
        # Fallback de texto se for mock ou URL local de testes
        message_content = prompt_text

    try:
        # Invoca o VLM
        result: ValidationOutput = structured_llm.invoke([HumanMessage(content=message_content)])
        
        logger.info(f"[VLM Node] Veredito: {result.verdict} | Modal: {result.detected_modality} | CO2: {result.co2_saved}kg")
        
        return {
            "verdict": result.verdict,
            "reasoning": result.reasoning,
            "co2_saved": result.co2_saved,
            "detected_modality": result.detected_modality,
            "estimated_distance_km": result.estimated_distance_km
        }
        
    except Exception as e:
        logger.error(f"[VLM Node] Erro critico de inferencia no VLM: {e}")
        return {
            "verdict": "REJECTED",
            "reasoning": "A auditoria automatizada do comprovante falhou temporariamente. Acao rejeitada preventivamente.",
            "co2_saved": 0.0,
            "detected_modality": None,
            "estimated_distance_km": None
        }
