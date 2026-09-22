package com.ecotrack.gamification.domain.dto;

import java.util.UUID;

/**
 * Record DTO para receber o payload de volta do motor de IA em Python.
 * Utilizado para mapear as decisões de antifraude e validação ESG.
 */
public record EvidenceResultEvent(
    UUID tenantId,
    UUID actionId,
    UUID userId,
    String actionType,
    String verdict, // APPROVED, REJECTED, FRAUD
    double estimatedCo2Saved,
    String aiReasoning
) {}
