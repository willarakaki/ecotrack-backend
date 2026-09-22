package com.ecotrack.gamification.api.controller;

import com.ecotrack.gamification.domain.dto.RedemptionRequest;
import com.ecotrack.gamification.domain.dto.RedemptionResponse;
import com.ecotrack.gamification.service.MarketplaceService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/marketplace")
public class MarketplaceController {

    private final MarketplaceService marketplaceService;

    public MarketplaceController(MarketplaceService marketplaceService) {
        this.marketplaceService = marketplaceService;
    }

    /**
     * Endpoint para troca de EcoCoins por Vouchers/Day-offs.
     * Header "X-User-Id" simula o token decodificado do API Gateway.
     */
    @PostMapping("/redemptions")
    public ResponseEntity<RedemptionResponse> redeemReward(
            @RequestHeader("X-User-Id") String userExternalId,
            @Valid @RequestBody RedemptionRequest request) {
            
        RedemptionResponse response = marketplaceService.redeemReward(userExternalId, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}
