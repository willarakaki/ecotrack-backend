package com.ecotrack.gamification.domain.dto;

import java.time.LocalDateTime;

public record RedemptionResponse(
        String redemptionId,
        String status,
        Double remainingBalance,
        LocalDateTime processedAt
) {}
