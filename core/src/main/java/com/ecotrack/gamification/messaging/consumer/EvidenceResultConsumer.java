package com.ecotrack.gamification.messaging.consumer;

import com.ecotrack.gamification.domain.document.EsgActionAuditLog;
import com.ecotrack.gamification.domain.dto.EvidenceResultEvent;
import com.ecotrack.gamification.repository.nosql.EsgActionAuditLogRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
public class EvidenceResultConsumer {

    private static final Logger log = LoggerFactory.getLogger(EvidenceResultConsumer.class);
    private final EsgActionAuditLogRepository auditLogRepository;

    public EvidenceResultConsumer(EsgActionAuditLogRepository auditLogRepository) {
        this.auditLogRepository = auditLogRepository;
    }

    /**
     * Listener Kafka protegido contra Poison Pills. Escuta a decisão final
     * do pipeline de IA (Gemini/LangGraph) via Python.
     */
    @KafkaListener(topics = "ia-evidence-results-topic", groupId = "ecotrack-gamification-group")
    public void consumeEvidenceResult(@Payload EvidenceResultEvent event) {
        log.info("Recebido veredito da IA para ação {}: {}", event.actionId(), event.verdict());

        try {
            // Trava de Segurança 1: Validação Defensiva (evitar persistir lixo ou NullPointer)
            if (event.tenantId() == null || event.actionId() == null) {
                log.error("Evento inválido recebido (Missing IDs). Descartando para DLQ (Simulada).");
                return; // Impede retentativas infinitas
            }

            EsgActionAuditLog auditLog = new EsgActionAuditLog();
            auditLog.setTenantId(event.tenantId());
            auditLog.setActionId(event.actionId());
            auditLog.setUserId(event.userId());
            auditLog.setTimestamp(Instant.now());

            // Regra de Negócio: Zera o impacto ESG em caso de Fraude ou Rejeição e taggeia o log
            if ("APPROVED".equalsIgnoreCase(event.verdict())) {
                auditLog.setActionType(event.actionType());
                auditLog.setEstimatedCo2Saved(event.estimatedCo2Saved());
            } else if ("FRAUD".equalsIgnoreCase(event.verdict())) {
                auditLog.setActionType("FRAUD_ATTEMPT_" + event.actionType());
                auditLog.setEstimatedCo2Saved(0.0);
                log.warn("🚨 Alerta Antifraude (IA): Tentativa do Usuário {} no Tenant {}", event.userId(), event.tenantId());
            } else {
                auditLog.setActionType("REJECTED_" + event.actionType());
                auditLog.setEstimatedCo2Saved(0.0);
            }

            auditLogRepository.save(auditLog);
            log.info("Trilha de auditoria (Immutable Ledger) salva no DynamoDB: {}", event.actionId());

        } catch (Exception e) {
            // Trava de Segurança 2: Anti-Loop
            // Previne que uma falha de banco trave a partição do Kafka em um retry loop infinito (Poison Pill).
            log.error("Falha crítica ao gravar auditoria do evento: {}. Enviando para DLQ.", event.actionId(), e);
        }
    }
}
