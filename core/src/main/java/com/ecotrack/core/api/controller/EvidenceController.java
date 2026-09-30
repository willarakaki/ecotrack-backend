package com.ecotrack.core.api.controller;

import com.ecotrack.core.api.dto.request.EvidenceRequest;
import com.ecotrack.core.messaging.event.EvidenceSubmittedEvent;
import com.ecotrack.core.messaging.publisher.EvidencePublisher;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.UUID;

@Slf4j
@RestController
@RequestMapping("/api/v1/evidences")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // Habilita o CORS pro frontend Next.js local
public class EvidenceController {

    private final EvidencePublisher evidencePublisher;

    @PostMapping
    public ResponseEntity<Void> submitEvidence(
            @RequestHeader(value = "X-Tenant-ID", defaultValue = "eco-tenant-1") String tenantId,
            @RequestHeader(value = "X-User-ID", defaultValue = "user-123") String userId,
            @RequestBody EvidenceRequest request) {

        log.info("Recebendo submissão de evidência ({}). Tenant: {}, User: {}", request.activityType(), tenantId, userId);
        
        String eventId = UUID.randomUUID().toString();
        
        // Monta o payload para o mensageiro (Apache Kafka) ir para a IA avaliar
        EvidenceSubmittedEvent event = new EvidenceSubmittedEvent(
                eventId,
                tenantId,
                userId,
                request.evidenceUrl() != null ? request.evidenceUrl() : "https://mock-url.com/img.jpg",
                request.activityType(),
                Instant.now()
        );

        // Publica no Kafka assincronamente e retorna 202 Accepted sem onerar a thread request-response
        evidencePublisher.publish(event);

        return ResponseEntity.accepted().build(); // 202 Accepted
    }
}
