package com.ecotrack.gamification.domain.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;

public record RedemptionRequest(
        @NotBlank(message = "O tipo de recompensa não pode estar vazio")
        String rewardType,
        
        @Positive(message = "O custo em EcoCoins deve ser maior que zero")
        Double costCoins
) {}
