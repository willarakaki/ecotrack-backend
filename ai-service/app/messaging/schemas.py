from pydantic import BaseModel
from typing import Optional

class EvidenceRequestEvent(BaseModel):
    """
    Representa o evento recebido do Core em Java (Spring Boot).
    Contém a foto/comprovante que a IA precisa analisar.
    """
    tenantId: str
    actionId: str
    userId: str
    actionType: str
    evidenceUrl: str # Pode ser URL do S3 ou Base64 (simplificado aqui)

class EvidenceResultEvent(BaseModel):
    """
    Representa o evento de resposta que o Python enviará de volta ao Java.
    Contém o veredito da IA e a quantificação de carbono.
    """
    tenantId: str
    actionId: str
    userId: str
    actionType: str
    verdict: str  # APPROVED, REJECTED, FRAUD
    estimatedCo2Saved: float
    aiReasoning: Optional[str] = None
