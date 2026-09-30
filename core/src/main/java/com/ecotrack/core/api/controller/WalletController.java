package com.ecotrack.core.api.controller;

import com.ecotrack.core.api.dto.request.CreditRequest;
import com.ecotrack.core.api.dto.request.TransferRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/wallet")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class WalletController {

    @PostMapping("/credit")
    public ResponseEntity<Void> credit(
            @RequestHeader(value = "X-Tenant-ID", defaultValue = "eco-tenant-1") String tenantId,
            @RequestBody CreditRequest request) {
        
        log.info("[Wallet] Creditando {} EcoCoins para o usuário do tenant {}. Motivo: {}", 
                 request.amount(), tenantId, request.reason());
                 
        // Aqui entraria a chamada ao WalletService com a entity User e Optimistic Locking.
        return ResponseEntity.ok().build();
    }

    @PostMapping("/transfer")
    public ResponseEntity<Void> transfer(
            @RequestHeader(value = "X-Tenant-ID", defaultValue = "eco-tenant-1") String tenantId,
            @RequestBody TransferRequest request) {
        
        log.info("[Wallet] P2P Transfer: {} EcoCoins enviados para {}. Tenant: {}. Tag: {}. Mensagem: {}", 
                 request.amount(), request.receiver(), tenantId, request.tag(), request.message());
                 
        // Aqui entraria a chamada ao WalletService para debitar e creditar com locks de saldo.
        return ResponseEntity.ok().build();
    }
}
