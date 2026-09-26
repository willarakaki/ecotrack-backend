from typing import TypedDict, Optional

class EvidenceValidationState(TypedDict):
    """
    Estado global que trafega entre os nós do nosso grafo (LangGraph).
    Ele é enriquecido passo a passo pelos agentes de IA.
    """
    action_id: str
    action_type: str
    evidence_url: str
    
    # Preenchidos dinamicamente pela LLM
    verdict: Optional[str]
    reasoning: Optional[str]
    co2_saved: Optional[float]
