package com.ecotrack.core.messaging.event;

import java.time.Instant;

// Payload enviado para o Router Python (LangGraph) avaliar a evidência
public record EvidenceSubmittedEvent(
        String eventId,
        String tenantExternalId,
        String userExternalId,
        String evidenceImageUrl,
        String actionType,
        Instant timestamp
) {}