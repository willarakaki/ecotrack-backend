package com.ecotrack.core.messaging.publisher;

import com.ecotrack.core.messaging.event.EvidenceSubmittedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class EvidencePublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private static final String TOPIC = "ia-evidence-requests-topic";

    public void publish(EvidenceSubmittedEvent event) {
        // Envio assÃ­ncrono para nÃ£o onerar o Core Transacional
        kafkaTemplate.send(TOPIC, event.eventId(), event)
                .whenComplete((result, ex) -> {
                    if (ex == null) {
                        log.info("Evento enviado com sucesso. Topic: {}, Offset: {}",
                                result.getRecordMetadata().topic(),
                                result.getRecordMetadata().offset());
                    } else {
                        log.error("Falha ao enviar evento para o motor de IA. EventId: {}. Causa: {}",
                                event.eventId(), ex.getMessage());
                        // Fallback (ex: DLQ ou alerta para DevOps) seria acionado aqui
                    }
                });
    }
}
