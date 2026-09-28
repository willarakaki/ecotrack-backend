from typing import TypedDict, Optional

class EvidenceValidationState(TypedDict):
    """
    Estado global que trafega entre os nos do nosso grafo (LangGraph).
    Ele e enriquecido passo a passo pelos agentes de IA.
    """
    action_id: str
    action_type: str
    evidence_url: str
    
    # Preenchidos dinamicamente pela LLM/VLM
    verdict: Optional[str]
    reasoning: Optional[str]
    co2_saved: Optional[float]
    detected_modality: Optional[str]
    estimated_distance_km: Optional[float]
