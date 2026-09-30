from pydantic import BaseModel, Field
from typing import Optional

class EvidenceRequestEvent(BaseModel):
    """
    Representa o evento recebido do Core em Java (Spring Boot).
    """
    tenantId: str = Field(alias="tenantExternalId")
    actionId: str = Field(alias="eventId")
    userId: str = Field(alias="userExternalId")
    actionType: str
    evidenceUrl: str = Field(alias="evidenceImageUrl")

    model_config = {
        "populate_by_name": True
    }

class EvidenceResultEvent(BaseModel):
    """
    Representa o evento de resposta que o Python enviara de volta ao Java.
    """
    tenantId: str
    actionId: str
    userId: str
    actionType: str
    verdict: str  # APPROVED, REJECTED, FRAUD
    estimatedCo2Saved: float
    aiReasoning: Optional[str] = None
