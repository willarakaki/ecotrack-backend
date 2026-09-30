package com.ecotrack.core.api.controller;

import com.ecotrack.core.api.dto.request.RedeemRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/marketplace")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class MarketplaceController {

    @PostMapping("/redeem")
    public ResponseEntity<Void> redeem(
            @RequestHeader(value = "X-Tenant-ID", defaultValue = "eco-tenant-1") String tenantId,
            @RequestBody RedeemRequest request) {
        
        log.info("[Marketplace] Usuário do tenant {} solicitou resgate do item '{}'. Custo: {} EcoCoins.", 
                 tenantId, request.rewardName(), request.cost());
                 
        // Aqui entraria a lógica de débito na Wallet e disparo de envio de cupom/email.
        return ResponseEntity.ok().build();
    }
}
